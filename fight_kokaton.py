import random
import sys
import time
import math

import pygame as pg


WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5  # 爆弾の数


def check_bound(obj_rct: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内or画面外を判定し，真理値タプルを返す関数
    引数：こうかとん，または，爆弾SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj_rct.left < 0 or WIDTH < obj_rct.right:
        yoko = False
    if obj_rct.top < 0 or HEIGHT < obj_rct.bottom:
        tate = False
    return yoko, tate


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -5),
        pg.K_DOWN: (0, +5),
        pg.K_LEFT: (-5, 0),
        pg.K_RIGHT: (+5, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        self.bird_img = pg.transform.rotozoom(
            pg.image.load("ex02/fig/3.png"), 
            0, 
            2.0
        )
        self.bird_img_reverse = pg.transform.rotozoom(
            pg.transform.flip(
                pg.image.load("ex02/fig/3.png"),
                False,
                True
            ), 
            0, 
            2.0
        )
        self.bird_img_list = {  # 8方向のこうかとんの辞書
            (0, -5): pg.transform.rotozoom(self.bird_img, -90, 1.0),
            (5, -5): pg.transform.rotozoom(self.bird_img_reverse, 225, 1.0),
            (5, 0): pg.transform.rotozoom(self.bird_img_reverse, 180, 1.0),
            (5, 5): pg.transform.rotozoom(self.bird_img_reverse, 135, 1.0),
            (0, 5): pg.transform.rotozoom(self.bird_img, 90, 1.0),
            (-5, 5): pg.transform.rotozoom(self.bird_img, 45, 1.0),
            (-5, 0): pg.transform.rotozoom(self.bird_img, 0, 1.0),
            (0, 0): pg.transform.rotozoom(self.bird_img, 0, 1.0),
            (-5, -5): pg.transform.rotozoom(self.bird_img, -45, 1.0),
            (0, 0): pg.transform.rotozoom(self.bird_img_reverse, 180, 1.0),
        }
        self.rct = self.bird_img.get_rect()
        self.rct.center = xy
        self.bird_img_res = None
        self.dire = (+5, 0)

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.img = pg.transform.rotozoom(pg.image.load(f"ex03/fig/{num}.png"), 0, 2.0)
        screen.blit(self.img, self.rct)

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        self.rct.move_ip(sum_mv)
        if check_bound(self.rct) != (True, True):
            self.rct.move_ip(-sum_mv[0], -sum_mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.bird_img_res = self.bird_img_list[tuple(sum_mv)]
        elif self.bird_img_res == None:
            self.bird_img_res = self.bird_img_list[(+5, 0)]

        self.dire = (sum_mv[0], sum_mv[1])
        screen.blit(self.bird_img_res, self.rct)


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self.img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.img, color, (rad, rad), rad)
        self.img.set_colorkey((0, 0, 0))
        self.rct = self.img.get_rect()
        self.rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self.vx, self.vy = +5, +5

    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(self.rct)
        if not yoko:
            self.vx *= -1
        if not tate:
            self.vy *= -1
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Beam:
    """
    ビームに関するクラス
    """
    last_angle_x = +5
    last_angle_y = 0

    def __init__(self, bird: Bird):
        """
        ビーム画像Surfaceを生成する
        引数1 bird：こうかとん画像の位置座標タプル
        """
        self.img = pg.image.load(f"ex03/fig/beam.png")
        self.rct = self.img.get_rect()
        vx, vy = bird.dire[0], bird.dire[1]
        if not (vx == 0 and vy == 0):
            self.vx, self.vy = vx, vy
            self.last_angle_x = vx
            self.last_angle_y = vy
        else:
            self.vx, self.vy = self.last_angle_x, self.last_angle_y
            
        angle = math.atan2(-vy, vx)
        self.img = pg.transform.rotozoom(self.img, math.degrees(angle), 1.0)
        self.rct.centerx = bird.rct.centerx + bird.rct.width * self.vx / 5
        self.rct.centery = bird.rct.centery + bird.rct.height * self.vy / 5

        
    def update(self, screen: pg.Surface):
        """
        ビームの位置を更新
        引数 screen：画面Surface
        """
        self.rct.move_ip(self.vx, self.vy)
        screen.blit(self.img, self.rct)


class Explosion:
    """
    ビームが爆弾に当たったときの爆発を描画する
    引数1 bomb：爆弾のSurface
    """
    def __init__(self, bomb: Bomb):
        self.explosion_img = pg.image.load("ex03/fig/explosion.gif")
        self.explosion_list = [
            pg.transform.flip(self.explosion_img, True, True),
            pg.transform.flip(self.explosion_img, True, False),
            pg.transform.flip(self.explosion_img, False, True),
            pg.transform.flip(self.explosion_img, False, False)
        ]
        self.rct = self.explosion_img.get_rect()
        self.rct.center = bomb.rct.center
        self.life = 30
    
    def update(self, screen: pg.Surface):
        self.life -= 1
        screen.blit(self.explosion_list[self.life % 4], self.rct)


class Score:
    """
    スコアを表示する
    引数1 bird：こうかとん画像の位置座標タプル
    """
    def __init__(self):
        self.font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 30)
        self.color = (0, 0, 255)
        self.score = 0
        self.img = self.font.render("スコア : " + str(self.score), 0, self.color)
        self.rct = self.img.get_rect()
        self.rct.centerx = 100
        self.rct.centery = HEIGHT - 50

    def update(self, score: int, screen: pg.Surface):
        self.score = score
        self.img = self.font.render("スコア : " + str(self.score), 0, self.color)
        screen.blit(self.img, self.rct)


def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))    
    bg_img = pg.image.load("ex03/fig/pg_bg.jpg")
    bird = Bird(3, (900, 400))
    # bomb = Bomb((255, 0, 0), 10)
    bombs = [Bomb((255, 0, 0), 10) for _ in range(NUM_OF_BOMBS)]
    explosions = []
    beams = []
    score = Score()

    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                # ビームクラスのインスタンスを生成
                beams.append(Beam(bird))
        
        screen.blit(bg_img, [0, 0])
        explosions = [explosion for explosion in explosions if explosion.life > 0]

        
        for bomb in bombs:
            if bird.rct.colliderect(bomb.rct):
                # ゲームオーバー時に，こうかとん画像を切り替え，1秒間表示させる
                bird.change_img(8, screen)
                pg.display.update()
                time.sleep(1)
                return
        
        for i, bomb in enumerate(bombs):
            for j, beam in enumerate(beams):
                if bomb is not None and beam is not None:
                    if beam.rct.colliderect(bomb.rct):
                        # ビームが爆弾に当たる
                        bombs[i] = None
                        beams[j] = None
                        bird.change_img(6, screen)
                        pg.display.update()
                        explosions.append(Explosion(bomb))
                        score.update(score.score + 1, screen)

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        bombs = [bomb for bomb in bombs if bomb is not None]
        beams = [beam for beam in beams if beam is not None]
        for bomb in bombs:
            if bomb is not None:
                bomb.update(screen)

        for i, beam in enumerate(beams):
            if beam is not None:
                beam.update(screen)
                if beam.rct.centerx < 0 or beam.rct.centerx > WIDTH or beam.rct.centery < 0 or beam.rct.centery > HEIGHT:
                    beams[i] = None
        
        beams = [beam for beam in beams if beam is not None]
        print(beams)
        for explosion in explosions:
            explosion.update(screen)

        score.update(score.score, screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
