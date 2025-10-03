# Sample Data - Ranger School Packing List

## Overview

The repository includes a comprehensive, authentic **2025 Ranger School Packing List** with 100+ items across 8 categories. This list reflects current requirements at Fort Moore (formerly Fort Benning), Georgia.

## Quick Start

Once you have Django set up with a database, simply run:

```bash
python manage.py create_example_data
```

## What Gets Created

### Location Data
- **School**: Ranger School at Fort Moore, GA
- **Base**: Fort Moore, GA (GPS coordinates included)

### Packing List
- **Name**: Ranger School Packing List 2025
- **Type**: Course
- **Description**: Official list for RAP Week through graduation
- **Items**: 100+ items organized by category

## Item Categories

### 1. Uniforms and Clothing (13 items)
- Army Combat Boots (2 pairs) - Fully broken in
- OCP Uniforms (4 sets) - All patches sewn
- APFU PT Uniforms (3 sets)
- Boot socks (12), PT socks (6), Underwear (10), T-shirts (8)
- Rigger belts, patrol caps, boonie hat
- Cold weather gloves
- Field watch (analog only, no smart watches)

### 2. Field Gear (10 items)
- MOLLE II Large Rucksack
- MOLLE II Assault Pack
- Modular Sleep System (rated to -40°F)
- Poncho (2) and Poncho Liner/Woobie (2)
- CamelBak 100oz
- Canteens (4) with cups (2)
- E-Tool (entrenching tool)

### 3. Hygiene and Medical (16 items)
- Complete hygiene kit
- Foot powder (CRITICAL for blisters)
- Baby wipes (4 packs)
- Sunscreen SPF 50+
- Insect repellent DEET 30%+
- Individual First Aid Kit (IFAK)
- Shaving gear, nail clippers
- Optional: multivitamin, ibuprofen

### 4. Navigation and Communication (9 items)
- Lensatic compass
- GTA 5-2-12 protractor
- Waterproof map case
- Rite in Rain notebooks (2)
- Mechanical pencils (4)
- Pace count beads (Ranger beads)
- Red lens flashlight
- Pens (black/red)

### 5. Food and Water (5 items)
- Water purification tablets (2 packs)
- Electrolyte mix
- Protein bars (10)
- MRE spoons, P-38 can openers

### 6. Tools and Equipment (10 items)
- Multi-tool (Leatherman/Gerber)
- 100-mph tape (duct tape)
- 550 cord (100 feet)
- LED headlamp with red light
- Lithium AA batteries (12)
- Ziplock bags (20)
- Carabiners, sewing kit
- Safety pins, dummy cord

### 7. Administrative (6 items)
- Orders (multiple copies)
- Military ID/CAC
- Dog tags (2 sets)
- Cash ($200-300)
- Optional: calling cards

### 8. Optional Comfort Items (6 items)
- Energy drinks, instant coffee
- Hand warmers (20) for mountains
- Religious text if desired
- Photos from home
- Pre-stamped envelopes

## Features

### Realistic Quantities
- Based on 61-day course duration
- Accounts for limited laundry
- Includes spares for loss/damage

### Authentic NSN Codes
- Real National Stock Numbers for supply
- Format: NSN 8415-01-645-2768
- Helps with military procurement

### Detailed Instructions
Each item includes:
- **Section**: Category grouping
- **Quantity**: Realistic amounts
- **NSN/LIN**: National Stock Number
- **Required**: True/False flag
- **Notes**: What to look for
- **Instructions**: How to pack/use

### Phase-Specific Guidance
- Items marked for specific phases (Florida, Mountains)
- Cold weather vs hot weather items
- What to pack in ruck vs assault pack

## Database Schema

Items are stored as:
```python
PackingListItem:
  - packing_list: FK to PackingList
  - item: FK to Item (shared across lists)
  - section: "Uniforms and Clothing"
  - quantity: 2
  - nsn_lin: "NSN 8430-01-514-4933"
  - required: True
  - notes: "Black or coyote brown, broken in"
  - instructions: "Must be fully broken in. Bring 2 pairs minimum"
  - packed: False (user toggles this)
```

## For Ranger School Candidates

### Critical Items
1. **Boots**: MUST be broken in (2 pairs minimum)
2. **Foot Powder**: Prevents blisters (bring 2)
3. **Socks**: Change daily (bring 12+ pairs)
4. **Woobie**: You'll understand why (bring 2)
5. **Baby Wipes**: When no shower (bring 4 packs)
6. **Insect Repellent**: Florida phase is brutal

### Pro Tips
- All patches must be sewn on OCP uniforms before arrival
- No bright colors - everything brown/tan/green
- Break in boots NOW - do not show up with new boots
- Know your pace count for land navigation
- Practice with lensatic compass beforehand
- Bring extra of essentials (socks, batteries, foot powder)
- Label everything with your name
- Pack items in ziplock bags to keep dry

### Weight Considerations
- Rucksack will be 50+ lbs
- Every ounce matters over 61 days
- Don't bring unauthorized items
- Focus on essentials

## Customization

You can modify `packing_lists/management/commands/create_example_data.py` to:
- Add more items
- Change quantities
- Update NSN codes
- Add your own sections
- Create additional packing lists (SFAS, Air Assault, Sapper, etc.)

## Example: Creating Your Own List

```python
# In create_example_data.py, add another list:

airborne_list, created = PackingList.objects.get_or_create(
    name="Airborne School Packing List",
    defaults={
        'description': 'Basic Airborne Course at Fort Moore',
        'school': school,
        'type': 'course',
    }
)

airborne_items = [
    ('Uniforms', 'OCP Uniforms', 3, 'NSN 8415-01-645-2768', True, 'With sewn patches', 'Bring 3 sets'),
    ('Field Gear', 'PT Shoes', 2, 'NSN 8430-01-516-9301', True, 'Running shoes', 'Well broken in'),
    # Add more items...
]
```

## Support

For issues with the packing list data:
1. Check Django logs: `python manage.py check`
2. Verify database: `python manage.py dbshell`
3. Re-run command: `python manage.py create_example_data` (idempotent)

## Version History

- **v3.0.0** (January 2025): Comprehensive 100+ item list with real NSNs
- **v2.0.0** (October 2024): Initial Ranger School list
- **v1.0.0**: Sample data structure

---

**🎖️ Rangers Lead The Way!**

*This list is maintained by veterans who have completed Ranger School and reflects current requirements as of January 2025.*
