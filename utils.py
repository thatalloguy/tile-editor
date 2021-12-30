import os



def scan_tiles():
    current_location = os.path.abspath(os.path.dirname(__file__))
    tiles_root = os.path.join(current_location, 'Tiles')
    for file_name in os.listdir(tiles_root):
        name, extension = os.path.splitext(file_name)
        if extension.lower() != '.png':
            continue
        tile_path = os.path.join('Tiles', file_name)
        yield name, tile_path
