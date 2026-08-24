# String Imager

String Imager turns an input image into a string-art style image. It preprocesses the source, finds a sequence of cords between points around a circle, and renders the resulting path. A run also saves the adjusted input, reconstructed image, path coordinates, best-value graph, progress images (when enabled), and an archive log.

## Setup

Use a recent Python installation. For the best performance with `--multi-threaded`, use a free-threaded Python build with the GIL disabled (Python 3.13+ `--disable-gil` build). The threaded optimizer can still run with the GIL enabled, but CPU-bound work will generally see less benefit.

Create and activate a virtual environment, then install the pinned dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate       # macOS/Linux
python -m pip install -r requirements.txt
```

Verify that the interpreter has the GIL disabled:

```bash
python -c "import sys; print('GIL enabled:', sys._is_gil_enabled())"
```

## Usage

View the program's help menu:

```bash
python main.py --help
```

Generate string art from an image:

```bash
python main.py solve path/to/image.png --multi-threaded
```

Results are written under `output/<image-name>/`; archived results and their parameters are written under `archive/`. Run `python main.py solve --help` to see all tuning options.

Render an existing path file again:

```bash
python main.py reconstruct output/<image-name>/path.txt
```
