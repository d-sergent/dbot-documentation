from setuptools import setup, find_packages

setup(
    name='dbot',
    version='0.1.0',
    description='D-Bot humanoid robot control package',
    author='David Sergent',
    packages=find_packages(),
    python_requires='>=3.10',
    install_requires=[
        'python-can>=4.2.0',
        'robstride>=0.1.0',
    ],
    extras_require={
        'vision': ['depthai>=2.24.0', 'flask>=2.0.0'],
        'audio':  [
            'pyaudio>=0.2.14', 
            'numpy>=1.24.0', 
            'SpeechRecognition>=3.10.0', 
            'gTTS>=2.4.0',
            'ollama>=0.1.7',
            'faster-whisper>=1.0.0',
            'piper-tts>=1.2.0'
        ],
    },
)
