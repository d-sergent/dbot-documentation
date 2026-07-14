"""
Test unitaire du client centralisé Qwen3-TTS depuis la Jetson.
Envoie une requête texte et joue la réponse audio reçue via le haut-parleur.
"""
import os
import sys
import asyncio

# Configuration PYTHONPATH pour retrouver les modules
WORKSPACE_DIR = "/Users/Shared/Mon Google Drive Physique/Documentation"
sys.path.append(os.path.join(WORKSPACE_DIR, "Code"))

from dbot_next.audio.tts_qwen3_central_client import Qwen3CentralClient

async def main():
    mac_ip = os.environ.get("DBOT_MAC_IP", "127.0.0.1")
    print(f"🚀 Démarrage du test centralisé. IP du Mac configurée : {mac_ip}")
    
    # Initialisation du client
    client = Qwen3CentralClient(host=mac_ip, port=8001)
    
    # Variable pour savoir quand quitter
    response_finished = asyncio.Event()
    
    def on_text(text):
        print(f"🤖 [D-Bot] : {text}")
        
    def on_end():
        print("✅ Fin de la réponse audio.")
        response_finished.set()
        
    client.on_text_received = on_text
    client.on_response_end = on_end
    
    # 1. Connexion au serveur central
    await client.connect()
    
    if not client._is_connected:
        print("\n❌ Impossible de se connecter au Mac compagnon.")
        print("Veuillez vérifier :")
        print("  1. Que le serveur tourne sur votre Mac : server_qwen3_central.py")
        print(f"  2. Que l'IP '{mac_ip}' est bien l'adresse IP réseau de votre Mac.")
        return

    # 2. Envoi de la phrase de test
    test_phrase = "Bonjour, ma voix du Mandalorien est maintenant configurée et opérationnelle."
    print(f"\n👤 Envoi de la phrase : '{test_phrase}'")
    
    await client.send_prompt(test_phrase)
    
    # 3. Attente de la fin de lecture
    try:
        await asyncio.wait_for(response_finished.wait(), timeout=15.0)
    except asyncio.TimeoutError:
        print("⚠ Timeout : pas de réponse reçue ou lecture bloquée.")
        
    client.close()
    print("🏁 Fin du test.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nInterrompu par l'utilisateur.")
