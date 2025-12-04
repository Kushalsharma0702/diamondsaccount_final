# T1 Form Schema Fix - Conditional Sub-Questions

## Problem

The T1 form has conditional sub-questions that are only relevant when certain boolean flags are true. The database schema wasn't properly validating these conditional requirements.

## Solution

Added comprehensive validators to handle conditional field requirements:

### 1. **Foreign Property Validation**
- When `hasForeignProperty = true` → `foreignProperties` array is required
- When `hasForeignProperty = false` → `foreignProperties` can be empty/null

### 2. **Moving Expenses Validation**
- When `hasMovingExpenses = true` and `movingExpenseForIndividual = true` → `movingExpenseIndividual` is required
- When `hasMovingExpenses = true` and `movingExpenseForSpouse = true` → `movingExpenseSpouse` is required

### 3. **Self Employment Validation**
- When `isSelfEmployed = true` → `selfEmployment` object is required
- When `businessTypes` includes `"uber"` → `uberBusiness` section is required
- When `businessTypes` includes `"general"` → `generalBusiness` section is required
- When `businessTypes` includes `"rental"` → `rentalIncome` section is required

### 4. **Other Income Validation**
- When `hasOtherIncome = true` → `otherIncomeDescription` is required

## Implementation

### Files Modified

1. **`client_side/shared/t1_enhanced_schemas.py`**
   - Added `@model_validator` to `T1PersonalFormBase` class
   - Added `@model_validator` to `T1SelfEmployment` class
   - Validators check conditional requirements based on boolean flags

### Validation Logic

```python
@model_validator(mode='after')
def validate_conditional_fields(self):
    """Validate all conditional field requirements based on boolean flags"""
    errors = []
    
    # Only validate when flags are explicitly True
    if self.hasForeignProperty is True:
        if not self.foreignProperties or len(self.foreignProperties) == 0:
            errors.append('foreignProperties array is required when hasForeignProperty is true')
    
    # ... more validations
    
    if errors:
        raise ValueError('Validation errors: ' + '; '.join(errors))
    
    return self
```

## Example Valid Form Structure

```json
{
  "personalInfo": {
    "firstName": "Jane",
    "lastName": "Doe",
    "sin": "123456789",
    "address": "123 Main St",
    "phoneNumber": "+14165550123",
    "email": "jane@example.com",
    "maritalStatus": "married"
  },
  "hasForeignProperty": true,
  "foreignProperties": [
    {
      "investmentDetails": "US ETF",
      "grossIncome": 1200.5,
      "country": "US"
    }
  ],
  "isSelfEmployed": true,
  "selfEmployment": {
    "businessTypes": ["uber", "general"],
    "uberBusiness": { /* required because "uber" in businessTypes */ },
    "generalBusiness": { /* required because "general" in businessTypes */ }
  }
}
```

## Testing

The validation will now properly handle:
- ✅ Conditional fields only required when flags are true
- ✅ Multiple business types requiring multiple sections
- ✅ Moving expenses for both individual and spouse
- ✅ Clear error messages when validation fails

## Next Steps

1. Test with sample JSON from `T1_Personal_sample.json`
2. Verify all conditional validations work correctly
3. Update API documentation with validation requirements

---

**Status:** ✅ Conditional validation implemented and ready for testing


