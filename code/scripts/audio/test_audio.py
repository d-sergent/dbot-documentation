#!/usr/bin/env python3
"""
scripts/audio/test_audio.py — Test ReSpeaker XVF-3800
=====================================================
Ce script vérifie la détection du ReSpeaker et tente d'enregistrer 
quelques secondes pour valider la capture.

Nécessite : pip install pyaudio
"""

import pyaudio
import wave
import sys
import subprocess

def list_audio_devices():
    p = pyaudio.PyAudio()
    print("\nCapture Devices détectés :")
    info = p.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    
    respeaker_index = None
    
    for i in range(0, num_devices):
        device_info = p.get_device_info_by_host_api_device_index(0, i)
        if device_info.get('maxInputChannels') > 0:
            name = device_info.get('name')
            print(f"  [{i}] {name} (canaux: {device_info.get('maxInputChannels')})")
            if "ReSpeaker" in name or "XVF3800" in name:
                respeaker_index = i
                
    p.terminate()
    return respeaker_index

def test_record(device_index, seconds=3):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 6  # Le XVF-3800 envoie souvent 6 canaux (4 micros + 2 reference/processed)
    RATE = 16000
    OUTPUT_FILE = "/tmp/test_audio.wav"
    
    p = pyaudio.PyAudio()
    
    try:
        # Essayer de détecter le nombre de canaux réel
        dev_info = p.get_device_info_by_index(device_index)
        CHANNELS = int(dev_info.get('maxInputChannels'))
        print(f"\nEnregistrement de {seconds}s sur {CHANNELS} canaux...")
        
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=device_index,
                        frames_per_buffer=CHUNK)
        
        frames = []
        for i in range(0, int(RATE / CHUNK * seconds)):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            
        print("✅ Enregistrement terminé.")
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        wf = wave.open(OUTPUT_FILE, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        print(f"💾 Fichier sauvegardé dans : {OUTPUT_FILE}")
        print("   (Vous pouvez le copier sur votre Mac pour l'écouter)")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'enregistrement : {e}")
        p.terminate()

def main():
    print("=" * 50)
    print("  D-Bot — Test Audio ReSpeaker")
    print("=" * 50)
    
    # Vérification lsusb
    print("Vérification USB...")
    try:
        lsusb = subprocess.run(['lsusb'], capture_output=True, text=True).stdout
        if "2886" in lsusb:
            print("✅ Seeed Studio (ReSpeaker) détecté en USB.")
        else:
            print("❌ ReSpeaker NON détecté en USB ! Vérifiez le branchement.")
            print("   (Note: Évitez le port USB-C sur Orin Nano, préférez l'USB-A bleu)")
            # On continue quand même pour voir ce que dit PyAudio
    except Exception:
        pass

    idx = list_audio_devices()
    
    if idx is not None:
        print(f"\n🎯 ReSpeaker trouvé à l'index {idx}")
        test_record(idx)
    else:
        print("\n❌ ReSpeaker non trouvé dans la liste des périphériques audio.")
        print("   Essayez d'installer 'pyaudio' : pip install pyaudio")

if __name__ == "__main__":
    main()
