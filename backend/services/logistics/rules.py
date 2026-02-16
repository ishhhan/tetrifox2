from schemas.domain import Parcel, InternalRule

class RuleEvaluator:
    @staticmethod
    def matches(parcel: Parcel, rule: InternalRule) -> bool:
        # 1. Dynamic Attribute Retrieval
        if not hasattr(parcel, rule.field):
            return False
        
        parcel_value = getattr(parcel, rule.field)

        # 2. Logic: Range Check (Numbers)
        if rule.type == "range":
            try:
                val = float(parcel_value)
                # Handle open-ended ranges (-inf to +inf)
                min_v = rule.min if rule.min is not None else float('-inf')
                max_v = rule.max if rule.max is not None else float('inf')
                
                # Logic: (min, max] -> min < val <= max
                is_above_min = val > min_v
                is_below_max = val <= max_v
                
                return is_above_min and is_below_max
            except (ValueError, TypeError):
                return False

        # 3. Logic: String Match
        if rule.type == "match":
            s_val = str(parcel_value).lower().strip()
            r_val = str(rule.match_value).lower().strip()
            return s_val == r_val

        return False
