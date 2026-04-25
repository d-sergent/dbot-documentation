import subprocess
import wave
import sys
import audioop

SAMPLE_RATE = 16000
CHANNELS = 2
DURATION = 5  # secondes
CHUNK_BYTES = int(SAMPLE_RATE * CHANNELS * 2) * DURATION  # 2 bytes par sample (S16_LE)

def test_split_channels():
    print("==================================================")
    print("  D-Bot — Séparation des Canaux Audio")
    print("==================================================")
    print("Lancement de l'enregistrement brut stéréo (5 secondes)...")
    print("🎤 Parlez maintenant !!")

    cmd = [
        "arecord",
        "-D", "hw:0,0",
        "-f", "S16_LE",
        "-r", str(SAMPLE_RATE),
        "-c", str(CHANNELS),
        "-d", str(DURATION),
        "-q"
    ]
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        raw_data, err = process.communicate()
    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)

    if not raw_data:
        print("❌ Aucun son capturé.")
        sys.exit(1)

    print("✅ Enregistrement terminé. Séparation des pistes...")

    # Extraction du canal 0 (Gauche)
    ch0_data = audioop.tomono(raw_data, 2, 1, 0)
    # Extraction du canal 1 (Droit)
    ch1_data = audioop.tomono(raw_data, 2, 0, 1)

    # Sauvegarde Canal 0
    with wave.open("canal_0_gauche.wav", 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(ch0_data)

    # Sauvegarde Canal 1
    with wave.open("canal_1_droit.wav", 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(ch1_data)

    print("✅ Fichiers sauvegardés :")
    print("   -> canal_0_gauche.wav")
    print("   -> canal_1_droit.wav")
    print("\nCopiez les deux fichiers sur votre Mac. L'un d'eux contiendra votre voix pure, l'autre du grésillement !")

if __name__ == "__main__":
    test_split_channels()
