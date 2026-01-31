"""
XML Parser Service with Deduplication and Missing Field Handling.

Parses XML content into domain Parcel objects, automatically
removing duplicates, handling missing fields, and logging warnings.
Returns parsing statistics for history tracking.
"""
import xml.etree.ElementTree as ET
from typing import List, Set, Dict, Tuple
from dataclasses import dataclass, field
from schemas.domain import Parcel
from schemas.parsing import ParsingStats, RemovedParcel
from core.exceptions import XmlParsingError
from core.config import logger


class XmlParserService:
    """Service for parsing XML parcel data into domain objects."""
    
    # Fields that should ideally be present
    EXPECTED_FIELDS = ['recipient', 'weight', 'value', 'city', 'street', 'postal_code']
    
    @staticmethod
    def parse_to_domain(xml_content: str) -> List[Parcel]:
        """
        Parse XML content and return unique Parcel objects.
        For backward compatibility, returns only the parcel list.
        Use parse_with_stats() to get both parcels and statistics.
        """
        parcels, _ = XmlParserService.parse_with_stats(xml_content)
        return parcels
    
    @staticmethod
    def parse_with_stats(xml_content: str) -> Tuple[List[Parcel], ParsingStats]:
        """
        Parse XML content and return unique Parcel objects with statistics.
        
        Features:
        - Extracts all Parcel elements from XML
        - Generates unique IDs for parcels
        - Removes duplicate parcels (by ID and content hash)
        - Handles missing fields with defaults
        - Logs warnings for duplicates and missing data
        
        Args:
            xml_content: Raw XML string
            
        Returns:
            Tuple of (list of unique Parcel objects, ParsingStats)
            
        Raises:
            XmlParsingError: If XML is malformed or parsing fails
        """
        try:
            root = ET.fromstring(xml_content)
            parcels: List[Parcel] = []
            seen_ids: Set[str] = set()
            seen_hashes: Dict[str, str] = {}  # Maps content hash to original parcel ID
            stats = ParsingStats()
            
            for p_elem in root.findall(".//Parcel"):
                stats.total_elements += 1
                parcel_counter = stats.total_elements
                
                # Generate parcel ID
                parcel_id = f"P{parcel_counter:03d}"
                
                # Check for existing ID attribute in XML
                xml_id = p_elem.get("id") or p_elem.findtext("Id") or p_elem.findtext("ID")
                if xml_id:
                    parcel_id = xml_id.strip()
                
                # ID-based deduplication check
                if parcel_id in seen_ids:
                    logger.warning(f"Duplicate parcel ID removed: {parcel_id}")
                    stats.duplicates_removed += 1
                    stats.duplicate_ids.append(parcel_id)
                    stats.removed_parcels.append(RemovedParcel(
                        parcel_id=parcel_id,
                        reason="duplicate_id",
                        details="Same ID already exists"
                    ))
                    continue
                
                # Helper to safely extract text with missing field tracking
                def get_text(parent, tag, default=None, field_name=None):
                    if parent is None:
                        if field_name:
                            stats.missing_fields[field_name] = stats.missing_fields.get(field_name, 0) + 1
                        return default
                    node = parent.find(tag)
                    if node is None or not node.text or not node.text.strip():
                        if field_name:
                            stats.missing_fields[field_name] = stats.missing_fields.get(field_name, 0) + 1
                        return default
                    return node.text.strip()

                missing_in_this_parcel = []
                
                # Parse nested structure with multiple spelling variations
                rec_node = (
                    p_elem.find("Receipient") or  # Common typo in XML
                    p_elem.find("Recipient") or
                    p_elem.find("recipient")
                )
                recipient = get_text(rec_node, "Name")
                if not recipient: missing_in_this_parcel.append("recipient")
                
                # Try multiple address spellings/locations
                addr_elem = (
                    rec_node.find("Address") if rec_node is not None else None
                ) or p_elem.find("Address") # Direct child fallback
                
                street = get_text(addr_elem, "Street")
                if not street: missing_in_this_parcel.append("street")
                
                city = get_text(addr_elem, "City")
                if not city: missing_in_this_parcel.append("city")
                
                postal_code = get_text(addr_elem, "PostalCode")
                if not postal_code:
                    # Try alternate spellings for postal code
                    postal_code = get_text(addr_elem, "Postal_Code")
                    if not postal_code:
                        postal_code = get_text(addr_elem, "ZipCode")
                        if not postal_code:
                            missing_in_this_parcel.append("postal_code")
                
                weight_str = get_text(p_elem, "Weight")
                if not weight_str: missing_in_this_parcel.append("weight")
                
                value_str = get_text(p_elem, "Value")
                if not value_str: missing_in_this_parcel.append("value")

                # If any critical fields are missing, discard and record
                if missing_in_this_parcel:
                    logger.warning(f"Parcel {parcel_id}: Discarded due to missing fields: {', '.join(missing_in_this_parcel)}")
                    for field in missing_in_this_parcel:
                        stats.missing_fields[field] = stats.missing_fields.get(field, 0) + 1
                    
                    stats.skipped_invalid += 1
                    stats.removed_parcels.append(RemovedParcel(
                        parcel_id=parcel_id,
                        reason="missing_field",
                        details=f"Missing: {', '.join(missing_in_this_parcel)}"
                    ))
                    continue

                # Parse numeric values
                try:
                    weight = float(weight_str)
                    if weight < 0:
                        logger.warning(f"Parcel {parcel_id}: Negative weight corrected to 0")
                        weight = 0
                except ValueError:
                    logger.warning(f"Parcel {parcel_id}: Invalid weight value '{weight_str}', discarding parcel.")
                    stats.skipped_invalid += 1
                    stats.removed_parcels.append(RemovedParcel(
                        parcel_id=parcel_id,
                        reason="invalid_value",
                        details=f"Invalid weight numeric format: '{weight_str}'"
                    ))
                    continue
                    
                try:
                    value = float(value_str)
                    if value < 0:
                        logger.warning(f"Parcel {parcel_id}: Negative value corrected to 0")
                        value = 0
                except ValueError:
                    logger.warning(f"Parcel {parcel_id}: Invalid value '{value_str}', discarding parcel.")
                    stats.skipped_invalid += 1
                    stats.removed_parcels.append(RemovedParcel(
                        parcel_id=parcel_id,
                        reason="invalid_value",
                        details=f"Invalid value numeric format: '{value_str}'"
                    ))
                    continue

                # Content-based deduplication (catch same data with different IDs)
                content_hash = f"{recipient}|{city}|{street}|{postal_code}|{weight}|{value}"
                if content_hash in seen_hashes:
                    original_id = seen_hashes[content_hash]
                    logger.warning(f"Duplicate content removed: {parcel_id} matches {original_id}")
                    stats.duplicates_removed += 1
                    stats.duplicate_ids.append(f"{parcel_id} → duplicate of {original_id}")
                    stats.removed_parcels.append(RemovedParcel(
                        parcel_id=parcel_id,
                        reason="duplicate_content",
                        details=f"Matches {original_id}"
                    ))
                    continue
                
                seen_ids.add(parcel_id)
                seen_hashes[content_hash] = parcel_id  # Map hash to this parcel ID
                
                parcels.append(Parcel(
                    id=parcel_id,
                    recipient=recipient,
                    street=street,
                    city=city,
                    postal_code=postal_code,
                    weight=weight,
                    value=value
                ))
                stats.valid_parcels += 1
            
            # Log parsing summary
            XmlParserService._log_parsing_summary(stats)
            
            return parcels, stats
            
        except ET.ParseError as e:
            raise XmlParsingError(f"XML Syntax Error: {str(e)}")
        except Exception as e:
            raise XmlParsingError(f"Parser Logic Error: {str(e)}")
    
    @staticmethod
    def _log_parsing_summary(stats: ParsingStats) -> None:
        """Log a summary of the parsing operation."""
        logger.info(
            f"XML Parsing Complete: {stats.valid_parcels}/{stats.total_elements} parcels parsed"
        )
        
        if stats.duplicates_removed > 0:
            logger.info(f"  - Removed {stats.duplicates_removed} duplicate(s)")
        
        if stats.skipped_invalid > 0:
            logger.warning(f"  - Skipped {stats.skipped_invalid} invalid parcel(s)")
        
        if stats.missing_fields:
            for field, count in stats.missing_fields.items():
                logger.warning(f"  - Missing '{field}' in {count} parcel(s)")