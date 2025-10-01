import csv
import glob

pattern = "size*_muros*_mover*.csv"
medias = {}

for filename in glob.glob(pattern):
    tiempos = []
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            tiempos.append(float(row["Tiempo (s)"]))
    if tiempos:
        medias[filename] = sum(tiempos) / len(tiempos)
    else:
        medias[filename] = 0.0

for file, media in sorted(medias.items()):
    print(f"{file}: {media:.6f} s")