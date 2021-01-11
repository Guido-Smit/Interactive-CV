from settings import *
import pytmx


def collide_hit_rect_to_rect(one, two):
    return one.hit_rect.colliderect(two.rect)

def collide_interact_rect_to_rect(one, two):
    return one.interact_rect.colliderect(two.rect)

def collide_interact_rect_to_interact_rect(one, two):
    return one.interact_rect.colliderect(two.interact_rect)

def collide_stop_rect_to_rect(one, two):
    if one is not two:
        return one.stop_rect.colliderect(two.rect)
    else:
        return False
def collide_hit_rects(one, two):
    return one.hit_rect.colliderect(two.hit_rect)

# This class can load txt map designs
class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename, "r") as f:
            for line in f:
                self.data.append(line.strip())

        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE

# This class can load maps met with the TILED application
class TiledMap:
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    # This render function checks which tiles are in the map and draws them on a surface with the blit option
    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth, y * self.tmxdata.tileheight))

    # This calls the render function to render all the tiles on a temporary surface which is then returned
    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface


class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, w, h, target):
        # move the camera around as the player moves
        x = -target.rect.centerx + int(w/2)
        y = -target.rect.centery + int(h/2)

        # limit the map scroll

        x = min(0, x) # The left map boundary
        y = min(0, y) # The top map boundary
        x = max(-(self.width - w), x) # The right map boundary
        y = max(-(self.height - h), y) # The bottom map boundary

        self.camera = pg.Rect(x, y, self.width, self.height)