
import pytest
from services.logistics.parser import XmlParserService

def test_parse_valid_xml():
    xml = """
    <Container>
        <Parcel>
            <Recipient>
                <Name>John Doe</Name>
                <Address>
                    <Street>Main St</Street>
                    <City>New York</City>
                    <PostalCode>10001</PostalCode>
                </Address>
            </Recipient>
            <Weight>10.5</Weight>
            <Value>100</Value>
        </Parcel>
    </Container>
    """
    parcels, stats = XmlParserService.parse_with_stats(xml)
    
    assert len(parcels) == 1
    assert stats.valid_parcels == 1
    assert parcels[0].recipient == "John Doe"
    assert parcels[0].weight == 10.5

def test_deduplication_by_id():
    xml = """
    <Container>
        <Parcel id="P001">
            <Recipient><Name>A</Name><Address><Street>S</Street><City>C</City><PostalCode>1</PostalCode></Address></Recipient>
            <Weight>1</Weight><Value>1</Value>
        </Parcel>
        <Parcel id="P001">
             <Recipient><Name>B</Name><Address><Street>S</Street><City>C</City><PostalCode>1</PostalCode></Address></Recipient>
            <Weight>1</Weight><Value>1</Value>
        </Parcel>
    </Container>
    """
    parcels, stats = XmlParserService.parse_with_stats(xml)
    
    assert len(parcels) == 1
    assert stats.duplicates_removed == 1
    assert "P001" in stats.duplicate_ids

def test_deduplication_by_content():
    xml = """
    <Container>
        <Parcel>
            <Recipient><Name>Same</Name><Address><Street>St</Street><City>Ct</City><PostalCode>1</PostalCode></Address></Recipient>
            <Weight>10</Weight><Value>10</Value>
        </Parcel>
        <Parcel>
            <Recipient><Name>Same</Name><Address><Street>St</Street><City>Ct</City><PostalCode>1</PostalCode></Address></Recipient>
            <Weight>10</Weight><Value>10</Value>
        </Parcel>
    </Container>
    """
    parcels, stats = XmlParserService.parse_with_stats(xml)
    
    assert len(parcels) == 1
    assert stats.duplicates_removed == 1

def test_negative_values_corrected():
    xml = """
    <Container>
        <Parcel>
            <Recipient><Name>A</Name><Address><Street>S</Street><City>C</City><PostalCode>1</PostalCode></Address></Recipient>
            <Weight>-5</Weight>
            <Value>-100</Value>
        </Parcel>
    </Container>
    """
    parcels, _ = XmlParserService.parse_with_stats(xml)
    
    assert parcels[0].weight == 0
    assert parcels[0].value == 0
