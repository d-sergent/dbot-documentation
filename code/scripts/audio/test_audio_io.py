"""
Test unitaire pour le module AudioIO (gestion des entrées/sorties audio).
"""

from dbot.audio.audio_io import AudioIO, AudioIOError

def test_audio_io():
    """
    Test unitaire pour AudioIO.

    Args:
        None

    Returns:
        bool: True si le test a réussi, False sinon.
    """
    try:
        # Initialisation
        print("🔄 [Test AudioIO] Initialisation du module AudioIO...")
        audio_io = AudioIO()

        # Test d'enregistrement
        print("🔄 [Test AudioIO] Test d'enregistrement (5 secondes)...")
        success = audio_io.record_audio(duration=5.0, output_file="/tmp/test_audio_io.wav")
        if not success:
            raise AudioIOError("[Test AudioIO] Échec de l'enregistrement.")

        # Test de lecture
        print("🔄 [Test AudioIO] Test de lecture...")
        success = audio_io.play_audio("/tmp/test_audio_io.wav")
        if not success:
            raise AudioIOError("[Test AudioIO] Échec de la lecture.")

        print("✅ [Test AudioIO] Test réussi !")
        return True
    except AudioIOError as e:
        print(f"❌ [Test AudioIO] Erreur : {e}")
        return False

if __name__ == "__main__":
    if test_audio_io():
        print("\n✅ Tous les tests ont réussi.")
    else:
        print("\n❌ Un ou plusieurs tests ont échoué.")