from django.db import migrations

def create_ranger_school_packing_list(apps, schema_editor):
    PackingList = apps.get_model('packing_lists', 'PackingList')
    PackingListItem = apps.get_model('packing_lists', 'PackingListItem')
    Item = apps.get_model('packing_lists', 'Item')

    list_name = "Ranger School Packing List V10"
    if not PackingList.objects.filter(name=list_name).exists():
        packing_list = PackingList.objects.create(
            name=list_name,
            description="Official Ranger School Packing List V10 as of Dec 2024"
        )

        items_data = [
            # (name, quantity, notes, nsn_lin)
            ("RUCKSACK LARGE FIELD PACK MOLLE", 1, "LIN: DA650J", "DA650J"),
            ("PACK FRAME MOLLE", 1, "LIN: DA650F", "DA650F"),
            ("SUSTAINMENT POUCH", 2, "LIN: DA650Y", "DA650Y"),
            ("MOLDED WAIST BELT", 1, "LIN: DA657T", "DA657T"),
            ("ENHANCED FRAME SHOULDER STRAPS MOLLE", 1, "LIN: DA652Z", "DA652Z"),
            ("BUCKLE MALE SHOULDER SUSPENSION", 1, "For Molle or CIF will issue Large Rucksack on Day 3 to all personnel needing one", None),
            ("LOAD LIFTER ATTACHMENT STRAP", 2, "LIN: DA657W", "DA657W"),
            ("HELMET, ADVANCED COMBAT", 1, "LIN: H53175", "H53175"),
            ("PAD SET, SUSPENSION", 1, "Must have all 7 Suspension Pads, nothing at all/7 pads during the layout will result in being dismissed", None),
            ("ACH BRACKET", 1, "", None),
            ("CAT-EYES BAND PAGST", 1, "LIN: YN1982", "YN1982"),
            ("COVER HELMET ACH MULTICAM-OR- COVER, HELMET, CAMO PATTERN", 1, "LIN: C2175C/C82472", "C2175C/C82472"),
            ("Eye Protection APEL (Clear Lens only) (w/inserts if required)", 1, "Minimum 1 pr.", None),
            ("MOLLE TACTICAL ASSAULT PANEL (TAP)", 1, "LIN: DA6690", "DA6690"),
            ("POUCH, 1 QT CANTEEN-GENERAL", 2, "LIN: DA5589", "DA5589"),
            ("POUCH, HAND GRENADE", 2, "LIN: DA5593", "DA5593"),
            ("POUCH, M4 TWO MAGAZINE", 2, "LIN: DA5582", "DA5582"),
            ("POUCH, M4 THREE MAG", 2, "LIN: DA5582", "DA5582"),
            ("FLASH BANG GRENADE POUCH", 1, "LIN: DA5693", "DA5693"),
            ("Compass, LENSATIC", 1, "NSN 6605-01-196-6971", "6605-01-196-6971"),
            ("Magazine, M4", 7, "30 round Magazine (ATRIB and CIF do not provide this item)", None),
            ("Adapter, fitting, M4 yellow, not M16 red", 1, "", None),
            ("CANTEEN 1QT", 2, "LIN: C9636", "C9636"),
            ("CANTEEN WATER 2QT", 1, "LIN: C9399", "C9399"),
            ("COVER, CANTEEN 2QT", 1, "LIN: DA6700", "DA6700"),
            ("CARRIER, HYDRATION SYSTEM W/BLADDER, HYDRATION S", 1, "LIN: DA650Z/DA6510", "DA650Z/DA6510"),
            ("GEN III - LEVEL1 LIGHTWEIGHT CW DRAWERS", 2, "LIN: D74128", "D74128"),
            ("GEN III - LEVEL2 MID-WEIGHT CW DRAWERS", 2, "", None),
            ("GEN III - LEVEL1 LW CW UNDERSHIRT", 2, "", None),
            ("GEN III - LEVEL2 MIDWEIGHT CW UNDERSHIRT", 2, "", None),
            ("GAITER NECK", 1, "", None),
            ("MITTEN INSERTS, COLD WEATHER", 2, "", None),
            ("MITTEN SHELLS, COLD WEATHER", 2, "", None),
            ("GLOVES COMBAT", 1, "LIN: DA154H", "DA154H"),
            ("WORK GLOVES, HEAVY DUTY", 1, "LIN: J68065", "J68065"),
            ("GLOVES, MEN'S AND WOMEN'S or GLOVES Flyers or Gloves Intermediate Cold Weather", 1, "LIN: DA153A or S06171", "DA153A/S06171"),
            ("OVERSHOES VINYL", 1, "NSN: N39848", "N39848"),
            ("BOOTS, INTERMEDIATE COLD WEATHER", 1, "", None),
            ("PONCHO WET WEATHER or TARPAULIN", 1, "LIN: P17415", "P17415"),
            ("LINER WET WEATHER PONCHO", 1, "LIN: L70789", "L70789"),
            ("EXTREME WET/COLD WEATHER JACKET LEVEL VI or item #124", 1, "LIN: E42924", "E42924"),
            ("Trousers Wet Weather or ECWCS Level IV Trousers or item #125", 1, "LIN: E43367", "E43367"),
            ("STUFF SACK, LRG", 1, "LIN: DA6597", "DA6597"),
            ("STUFF SACK, SML", 1, "LIN: DA6553U", "DA6553U"),
            ("BIVY COVER, MODULAR SYSTEM", 1, "LIN: DA658R", "DA658R"),
            ("SLEEPING BAG ICW (Winter-Gray)", 1, "LIN: DA658N", "DA658N"),
            ("SLEEPING BAG-(Patrol-Green)", 1, "LIN: DA658Z", "DA658Z"),
            ("CAP, PATROL, ARMY COMBAT UNIFORM", 1, "LIN: C02082", "C02082"),
            ("Coat, ACU OCP (must have minimum of 2 winter uniforms the others can be Coat, IHWCU)", 4, "LIN: C68926", "C68926"),
            ("Trousers, ACU OCP (must have a minimum of 2 winter uniforms the others can be Trousers, IHWCU)", 4, "LIN: T057108", "T057108"),
            ("T-Shirts, S/S; Tan 499; loose fitting", 7, "", None),
            ("Belt, brown non-elastic (trigger style)", 7, "", None),
            ("Socks, cushion sole wool blend (military black, tan or green - non waterproof)", 7, "", None),
            ("Boots, Hot Weather Desert (IAW DA PAM 670-1 with no buckles)", 2, "", None),
            ("PT Uniform: Jacket, Pants, Long Sleeve Shirt, Short Sleeve Shirt, Shorts", 1, "", None),
            ("Socks, white/black (calf or above ankle only)", 2, "", None),
            ("WATCH CAP: BLACK MICRO FLEECE", 1, "LIN: C03291", "C03291"),
            ("Belt, reflective (high vis. yellow)", 1, "", None),
            ("PT Shoes", 1, "", None),
            ("Ear Plugs with Case, Triple Flange minimum", 1, "", None),
            ("Protractor", 1, "GTA 5-2-12", None),
            ("Razor, shaving (non electric)", 1, "", None),
            ("Razor Blades", 12, "", None),
            ("Alcohol Marker, permanent (4 pack multiple colors)", 1, "", None),
            ("Camouflage Stick (or like item)", 3, "NSN 6850-00-161-6204", "6850-00-161-6204"),
            # ... Add more items as needed from the PDF ...
        ]

        for name, quantity, notes, nsn_lin in items_data:
            item_obj, _ = Item.objects.get_or_create(name=name)
            PackingListItem.objects.get_or_create(
                packing_list=packing_list,
                item=item_obj,
                defaults={
                    'quantity': quantity,
                    'notes': notes or "",
                    'nsn_lin': nsn_lin or "",
                    'required': True,
                }
            )

class Migration(migrations.Migration):
    dependencies = [
        ('packing_lists', '0008_store_url'),
    ]
    operations = [
        migrations.RunPython(create_ranger_school_packing_list),
    ] 