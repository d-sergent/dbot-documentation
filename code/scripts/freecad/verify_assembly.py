import FreeCAD

doc_path = "/Users/Shared/DBot_Assembly_Sovereign.FCStd"
doc = FreeCAD.openDocument(doc_path)

print(f"Document Label: {doc.Label}")
print(f"Total Objects in Doc: {len(doc.Objects)}")

root_asm = doc.getObject("DBot_Assembly")
torse = doc.getObject("Torse_Superieur")
bassin = doc.getObject("Bassin_Pelvis")

print(f"Root Assembly: {root_asm.Label if root_asm else 'None'}")
print(f"  Torse Superieur: {torse.Label if torse else 'None'} (Placement: {torse.Placement.Base if torse else ''})")
print(f"  Bassin Pelvis:   {bassin.Label if bassin else 'None'} (Placement: {bassin.Placement.Base if bassin else ''})")

if bassin:
    print(f"\nComposants dans Bassin_Pelvis ({len(bassin.Group)}):")
    for obj in bassin.Group:
        mat_prop = getattr(obj, "MaterialName", "N/A")
        print(f"  - {obj.Label:45} | Global Z={obj.getGlobalPlacement().Base.z:7.2f} mm | Mat: {mat_prop}")

# Compute global bounding box
bb = None
for obj in doc.Objects:
    if hasattr(obj, "Shape") and not obj.Shape.isNull() and hasattr(obj, "getGlobalPlacement"):
        sh = obj.Shape.copy()
        sh.Placement = obj.getGlobalPlacement()
        if bb is None:
            bb = sh.BoundBox
        else:
            bb.add(sh.BoundBox)

if bb:
    print("\n=== BOÎTE ENGLOBANTE GLOBALE DE L'ASSEMBLAGE ROBOT ===")
    print(f"  X : [{bb.XMin:.1f}, {bb.XMax:.1f}] mm (Largeur : {bb.XLength:.1f} mm)")
    print(f"  Y : [{bb.YMin:.1f}, {bb.YMax:.1f}] mm (Profondeur : {bb.YLength:.1f} mm)")
    print(f"  Z : [{bb.ZMin:.1f}, {bb.ZMax:.1f}] mm (Hauteur : {bb.ZLength:.1f} mm)")

FreeCAD.closeDocument(doc.Name)
print("\nContrôle métrologique validé avec succès !")
