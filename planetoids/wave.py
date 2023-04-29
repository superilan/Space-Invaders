"""
Subcontroller module for Planetoids

This module contains the subcontroller to manage a single level (or wave) in the 
Planetoids game.  Instances of Wave represent a single level, and should correspond
to a JSON file in the Data directory. Whenever you move to a new level, you are 
expected to make a new instance of the class.

The subcontroller Wave manages the ship, the asteroids, and any bullets on screen. These 
are model objects. Their classes are defined in models.py.

Most of your work on this assignment will be in either this module or models.py.
Whether a helper method belongs in this module or models.py is often a complicated
issue.  If you do not know, ask on Ed Discussions and we will answer.

Aaron Baruch Ilan Klimberg
12/7/2022
"""
from game2d import *
from consts import *
from models import *
import random
import datetime

# PRIMARY RULE: Wave can only access attributes in models.py via getters/setters
# Level is NOT allowed to access anything in app.py (Subcontrollers are not permitted
# to access anything in their parent. To see why, take CS 3152)


class Wave(object):
    """
    This class controls a single level or wave of Planetoids.
    
    This subcontroller has a reference to the ship, asteroids, and any bullets on screen.
    It animates all of these by adding the velocity to the position at each step. It
    checks for collisions between bullets and asteroids or asteroids and the ship 
    (asteroids can safely pass through each other). A bullet collision either breaks
    up or removes a asteroid. A ship collision kills the player. 
    
    The player wins once all asteroids are destroyed.  The player loses if they run out
    of lives. When the wave is complete, you should create a NEW instance of Wave 
    (in Planetoids) if you want to make a new wave of asteroids.
    
    If you want to pause the game, tell this controller to draw, but do not update.  See
    subcontrollers.py from Lecture 25 for an example.  This class will be similar to
    than one in many ways.
    
    All attributes of this class are to be hidden. No attribute should be accessed 
    without going through a getter/setter first. However, just because you have an
    attribute does not mean that you have to have a getter for it. For example, the
    Planetoids app probably never needs to access the attribute for the bullets, so 
    there is no need for a getter there. But at a minimum, you need getters indicating
    whether you one or lost the game.
    """
    # LIST ANY ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
    # THE ATTRIBUTES LISTED ARE SUGGESTIONS ONLY AND CAN BE CHANGED AS YOU SEE FIT
    # Attribute _data: The data from the wave JSON, for reloading 
    # Invariant: _data is a dict loaded from a JSON file
    #
    # Attribute _ship: The player ship to control 
    # Invariant: _ship is a Ship object
    #
    # Attribute _asteroids: the asteroids on screen 
    # Invariant: _asteroids is a list of Asteroid, possibly empty
    #
    # Attribute _bullets: the bullets currently on screen 
    # Invariant: _bullets is a list of Bullet, possibly empty
    #
    # Attribute _lives: the number of lives left 
    # Invariant: _lives is an int >= 0
    #
    # Attribute _firerate: the number of frames until the player can fire again 
    # Invariant: _firerate is an int >= 0
    #
    # Attribute _allDestroyed: True if all of the asteroids have been destroyed,
    # False otherwise
    # Invariant: _allDestroyed is a bool True or False
    
    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
   
    def getLives(self):
        """
        Returns remaining lives.
        """
        return self._lives
    
    def getAsteroids(self):
        """
        Returns asteroids list.
        """
        return self._asteroids
    
    def getAllDestroyed(self):
        """
        Returns bool declaring if all asteroids have been destroyed.
        """
        return self._allDestroyed
    
    # INITIALIZER (standard form) TO CREATE SHIP AND ASTEROIDS
    def __init__(self, json, lives, start, asteroids=None):
        """
        Initializes a new Wave with the given JSON dictionary containing 
        all of the information about the ship. Sets initial asteroids
        (when the game first starts), or current asteroids (when the 
        game continues after the player has died), bullets, firereate, 
        lives, and allDestroyed bool.

        Parameter json: the json file containing all of the information 
        about the wave.
        Precondition: json is a dict loaded from a JSON file.

        Parameter lives: current value of lives left in the wave.
        Precondition: lives is an int.

        Parameter start: indicates whether the wave is being started 
        for the first time.
        Precondition: start is a bool True or False.

        Parameter asteroids: Current asteroids in the wave after the 
        player has died.
        Precondition: asteroids is a list of Asteroid objects, possibly 
        empty
        """
        self._makeShip(json)
        self._bullets = []
        self._firerate = 0
        self._lives = lives
        self._allDestroyed = False
        if start:
            self._asteroids = self._addAsteroids()
        else:
            self._asteroids = asteroids

    # UPDATE METHOD TO MOVE THE SHIP, ASTEROIDS, AND BULLETS
    def update(self, dt, input):
        """
        Animates the ship, asteroids, and bullets.

        Parameter dt: The time in seconds since last update
        Precondition: dt is a number (int or float)

        Parameter input: the user input, used to control the ship and 
        change state.
        Precondition: input is an instance of GInput.
        """
        if not self._ship is None:
            if input.is_key_down('left'):
                self._ship.angle += SHIP_TURN_RATE
                self._ship.turn(self._ship.angle)
            if input.is_key_down('right'):
                self._ship.angle -= SHIP_TURN_RATE
                self._ship.turn(self._ship.angle)
            if input.is_key_down('spacebar') and self._firerate >= BULLET_RATE:
                self._addBullets()
            self._ship.thrust(input)
            self._wrap(self._ship)
            for asteroid in self._asteroids:
                asteroid.move()
                self._wrap(asteroid)
            self._firerate += 1
            for bullet in self._bullets:
                bullet.move()
            i = 0
            while i < len(self._bullets):
                if self._bullets[i].isOut():
                    del self._bullets[i]
                else:
                    i += 1
            self._collisions()
    
    # DRAW METHOD TO DRAW THE SHIP, ASTEROIDS, AND BULLETS
    def draw(self, view):
        """
        Draws the ship, asteroids, and bullets objects to the game view 
        provided.

        Parameter view: the game view
        Precondition: view is an instance of GView
        """
        if not self._ship is None:
            self._ship.draw(view)
        for asteroid in self._asteroids:
            asteroid.draw(view)
        for bullet in self._bullets:
            bullet.draw(view)

    # RESET METHOD FOR CREATING A NEW LIFE
    # HELPER METHODS FOR PHYSICS AND COLLISION DETECTION
    def decrementLives(self):
        """
        Decrements _lives attribute by 1.
        """
        self._lives -= 1

    def shipDied(self):
        """
        Returns True if the ship Died. Returns False if the ship did not die.
        We know ship died if _ship is None.
        """
        return self._ship is None

    def _makeShip(self, json):
        """
        Instantiates a new ship object using the data from the JSON
        dictionary.

        Parameter json: the json file containing all of the information 
        about the wave.
        Precondition: json is a dict loaded from a JSON file.
        """
        self._data = json
        self._ship = Ship(x=self._data["ship"]["position"][0],\
            y=self._data["ship"]["position"][1],\
            angle=self._data["ship"]["angle"],source=SHIP_IMAGE,\
            width=(2*SHIP_RADIUS),height=(2*SHIP_RADIUS))

    def _wrap(self, value):
        """
        Wraps the ships and asteroids across the game view screen. Uses 
        DEAD_ZONE constant to smoothly wrap from one side to another, if
        the object's x or y attribute crosses the threshold. 

        Parameter value: the ship or asteroid object to wrap.
        Precondition: value is a ship or asteroid object.
        """
        if value.x > GAME_WIDTH+DEAD_ZONE:
            value.x = value.x - (GAME_WIDTH+2*DEAD_ZONE)
        if value.x < -DEAD_ZONE:
            value.x = value.x + (GAME_WIDTH+2*DEAD_ZONE)
        if value.y > GAME_HEIGHT+DEAD_ZONE:
            value.y = value.y - (GAME_HEIGHT+2*DEAD_ZONE)
        if value.y < -DEAD_ZONE:
            value.y = value.y + (GAME_HEIGHT+2*DEAD_ZONE)

    def _addAsteroids(self):
        """
        Returns a list of the Asteroid objects to be added to
        the _asteroids attribute (list) by looping 
        through the _data dictionary in the "asteroids" key.

        Obtains the necessary attributes from the dictionary to assign to the 
        Asteroid objects being added to the list.
        """
        result = []
        for i in range(len(self._data["asteroids"])):
            if self._data["asteroids"][i]["size"] == SMALL_ASTEROID:
                result.append(Asteroid(\
                    x=self._data["asteroids"][i]["position"][0],\
                    y=self._data["asteroids"][i]["position"][1],\
                    source=SMALL_IMAGE,width=(2*SMALL_RADIUS),\
                    height=(2*SMALL_RADIUS),size=SMALL_ASTEROID,\
                    direction=self._data["asteroids"][i]["direction"]))
            elif self._data["asteroids"][i]["size"] == MEDIUM_ASTEROID:
                result.append(Asteroid(\
                    x=self._data["asteroids"][i]["position"][0],\
                    y=self._data["asteroids"][i]["position"][1],\
                    source=MEDIUM_IMAGE,width=(2*MEDIUM_RADIUS),\
                    height=(2*MEDIUM_RADIUS),size=MEDIUM_ASTEROID,\
                    direction=self._data["asteroids"][i]["direction"]))
            elif self._data["asteroids"][i]["size"] == LARGE_ASTEROID:
                result.append(Asteroid(\
                    x=self._data["asteroids"][i]["position"][0],\
                    y=self._data["asteroids"][i]["position"][1],\
                    source=LARGE_IMAGE,width=(2*LARGE_RADIUS),\
                    height=(2*LARGE_RADIUS),size=LARGE_ASTEROID,\
                    direction=self._data["asteroids"][i]["direction"]))
        return result

    def _addBullets(self):
        """
        Adds the Bullet objects to the _bullets attribute (list) by 
        calulating the tip of the ship to find the corresponding 
        x any y position of the bullet.

        Sets bullet _firerate to 0.
        """
        shipPos = introcs.Vector2(self._ship.x,self._ship.y)
        tip = (self._ship.getFacing().normal() * SHIP_RADIUS) + shipPos
        self._bullets.append(Bullet(x=tip.x,y=tip.y,\
            fillcolor=BULLET_COLOR,width=2*BULLET_RADIUS,\
            height=2*BULLET_RADIUS,\
            facing=self._ship.getFacing().normal()))
        self._firerate = 0

    def _doesCollide(self, asteroid, other):
        """
        Returns True if the distance between the positions of two objects
        is less than the sum of their radii, meaning that they collide.

        Parameter asteroid: the asteroid to that is being checked for collision
        Precondition: asteroid is an Asteroid object

        Parameter other: the object (ship or bullet) being checked for collision
        Precondition: other is either a Ship or Bullet object
        """
        distance = ((asteroid.x - other.x)**2 + (asteroid.y - other.y)**2)**0.5
        if distance < (asteroid.width/2 + other.width/2):
            return True
        else:
            return False

    def _collisions(self):
        """
        Gathers data from _collisionData method.

        If an asteroid collided with the ship or a bullet, sets the 
        resultantVector1 and resultantVector2 and splits the asteroids. 
        Resultant vectors are used to determine the direction and position
        of split asteroids. Sets _allDestroyed to True if all asteroids 
        are destroyed.
        """
        mediumDeleted = 0
        largeDeleted = 0
        collisionVector = None
        oldX = 0
        oldY = 0
        data=self._collisionData\
            (mediumDeleted, largeDeleted, collisionVector, oldX, oldY, i=0)
        mediumDeleted = data[0]
        largeDeleted = data[1]
        collisionVector = data[2]
        oldX = data[3]
        oldY = data[4]
        if not collisionVector is None:
            resultantVector1 = self._makeResultantVector1(collisionVector)
            resultantVector2 = self._makeResultantVector2(collisionVector)
            self._splitLargeAsteroid\
                (largeDeleted, oldX, oldY,\
                collisionVector, resultantVector1, resultantVector2)
            self._splitMediumAsteroid\
                (mediumDeleted, oldX, oldY,\
                collisionVector, resultantVector1, resultantVector2)
        if len(self._asteroids) == 0:
            self._allDestroyed = True 

    def _collisionData(self, mediumDeleted,\
        largeDeleted, collisionVector, oldX, oldY, i):
        """
        Returns a list of mediumDeleted, largeDeleted, collisionVector, oldX, 
        oldY, and i for _collisions() function.

        Iterates through asteroids and bullets to see if the two have collided. 
        If they collide then the bullet and asteroid that collided are deleted.

        Iterates through asteroids again to see if the asteroid
        collides with ship. If so then the asteroid and the ship are 
        deleted, the ship being set to None.

        When collisions occur, a collisionVector is calculated and the
        center position of the deleted asteroid is saved so they can be used in 
        creating the split asteroids.

        Parameter mediumDeleted: the amount of medium asteroids that need to be 
        deleted. This parameter is also used to determine how many medium 
        asteroids need to be broken up into small asteroids.
        Precondition: mediumDeleted is an int >= 0.

        Parameter largeDeleted: the amount of large Asteroids that need to be 
        deleted. This parameter is also used to determine how many large 
        asteroids need to be broken up into medium asteroids.
        Precondition: largeDeleted is an int >= 0.

        Parameter collisionVector: the vector created from 
        the collision of a bullet and an asteroid
        or from the collision of a ship and an asteroid.
        Precondition: collisionVector is a Vector2 object or None.

        Parameter oldx: the x position of the colliding Asteroid's center.
        Precondition: oldX is an int or float.

        Parameter oldY: the y position of the colliding Asteroid's center.
        Precondition: oldY is an int or float.

        Parameter i: the variable used to iterate through the while loop.
        Precondition i: i is an int 0.
        """
        while i<len(self._asteroids):
            n=0
            while n<len(self._bullets) and self._asteroids[i].getDel()==False:
                if self._doesCollide(self._asteroids[i],self._bullets[n]):
                    collisionVector=self._bullets[n].getVelocity().normal()
                    oldX=self._asteroids[i].x; oldY = self._asteroids[i].y
                    del self._bullets[n]
                    self._asteroids[i].setDel(True)
                else: n+=1
            if self._asteroids[i].getDel()==True:
                if self._asteroids[i].getSize()=='large': largeDeleted+=1 
                elif self._asteroids[i].getSize()=='medium': mediumDeleted+=1
                del self._asteroids[i]
            else: i+=1
        i=0
        while i<len(self._asteroids) and not self._ship is None:
            if not (self._asteroids[i].getDel()==True):
                if self._doesCollide(self._asteroids[i],self._ship):
                    if self._ship.getVelocity()==introcs.Vector2(0,0):
                        collisionVector=self._ship.getFacing()
                        oldX=self._asteroids[i].x; oldY=self._asteroids[i].y
                    else:
                        collisionVector=self._ship.getVelocity().normal()
                        oldX=self._asteroids[i].x; oldY=self._asteroids[i].y
                    self._shipColSplit(mediumDeleted,\
                        largeDeleted, collisionVector, i, oldX, oldY)
                else: i+=1
        return [mediumDeleted, largeDeleted, collisionVector, oldX, oldY]  

    def _shipColSplit(self, mediumDeleted, largeDeleted, \
        collisionVector, i, oldX, oldY):
        """
        Splits the asteroid at index i in the _asteroids list, that has
        collided with the ship. If the asteroid is large, it splits into 
        three medium asteroids. If the asteroid is medium, it splits into 
        three small asteroids. The asteroid that collides with ship is 
        then deleted and the ship is set to None.

        Parameter mediumDeleted: the amount of mediumAsteroids that need to 
        be deleted. This parameter is also used to determine how many medium 
        asteroids need to be broken up into small asteroids.
        precondition: mediumDeleted is an int

        Parameter largeDeleted: the amount of largeAsteroids that need 
        to be deleted. This parameter is also used to determine how many large 
        asteroids need to be broken up into medium asteroids.
        precondition: largeDeleted is an int

        Parameter collisionVector: the vector created from 
        the collision of a bullet and an asteroid
        or from the collision of a ship and an asteroid.
        Precondition: collisionVector is a Vector2 object

        Parameter i: the variable used to iterate through the while loop
        in _collisionData()
        Precondition i: i is an int 0

        Parameter oldx: the previous x position of the Asteroid center.
        precondition: oldX is an int or float

        Parameter oldY: the previous y position of the Asteroid center.
        precondition: oldY is an int or float
        """
        self._asteroids[i].setDel(True)
        resultantVector1 = self._makeResultantVector1(collisionVector)
        resultantVector2 =self._makeResultantVector2(collisionVector)
        if self._asteroids[i].getSize() == 'large':
            largeDeleted += 1
            self._splitLargeAsteroid(largeDeleted, oldX, oldY,\
                collisionVector, resultantVector1, resultantVector2)
        if self._asteroids[i].getSize() == 'medium':
            mediumDeleted += 1
            self._splitMediumAsteroid(mediumDeleted, oldX, oldY,\
        collisionVector, resultantVector1, resultantVector2)
        del self._asteroids[i]
        self._ship=None 
    
    def _makeResultantVector1(self,collisionVector):
        """
        Returns resultantVector1, the vector we calculate using collisionVector.

        Asteroids split due to collisions with bullets or a collision with the 
        ship. When asteroids are split up, resultantVector1 is collisionVector 
        but rotated 120 degrees. 

        Parameter collisionVector: the vector created from 
        the collision of a bullet and an asteroid
        or from the collision of a ship and an asteroid.
        Precondition: collisionVector is a Vector2 object.
        """
        rad = degToRad(120.0)
        resultantVector1 = introcs.Vector2\
            ((collisionVector.x * math.cos(rad) - \
            collisionVector.y * math.sin(rad)),\
            (collisionVector.x * math.sin(rad) + \
            collisionVector.y * math.cos(rad)))
        resultantVector1.normal()
        return resultantVector1

    def _makeResultantVector2(self,collisionVector):
        """
        Returns resultantVector2, the vector we calculate using 
        collisionVector. 

        Asteroids split due to collisions with bullets or a collision with the
        ship. When asteroids are split up, resultantVector2 is collisionVector 
        but rotated -120 degrees. 

        Parameter collisionVector: the vector created from 
        the collision of a bullet and an asteroid
        or from the collision of a ship and an asteroid.
        Precondition: collisionVector is a Vector2 object.
        """
        rad = degToRad(-120.0)
        resultantVector2 = introcs.Vector2\
            ((collisionVector.x * math.cos(rad) - \
            collisionVector.y * math.sin(rad)),\
            (collisionVector.x * math.sin(rad) + \
            collisionVector.y * math.cos(rad)))
        resultantVector2.normal()
        return resultantVector2

    def _splitLargeAsteroid(self, largeDeleted, oldX, oldY,\
        collisionVector, resultantVector1, resultantVector2):
        """
        Splits a large asteroid into three medium asteroids.

        Parameter largeDeleted: the amount of large Asteroids that need to be 
        deleted. This parameter is also used to determine how many large 
        asteroids need to be broken up into medium asteroids.
        Precondition: largeDeleted is an int >= 0.

        Parameter oldx: the x position of the colliding Asteroid's center.
        Precondition: oldX is an int or float.

        Parameter oldY: the y position of the colliding Asteroid's center.
        Precondition: oldY is an int or float.

        Parameter collisionVector: the vector created from 
        the collision of a bullet and an asteroid
        or from the collision of a ship and an asteroid.
        Precondition: collisionVector is a Vector2 object or None.

        Parameter resultantVector1: resultantVector1 is collisionVector 
        but rotated 120 degrees. 
        precondition: resultantVector1 is a Vector2 object.

        Parameter resultantVector2: resultantVector1 is collisionVector 
        but rotated -120 degrees. 
        Precondition: resultantVector2 is a Vector2 object.
        """
        for i in range(largeDeleted):
            center = MEDIUM_RADIUS*collisionVector
            xandyList = [oldX+center.x, oldY+center.y]
            self._asteroids.append(Asteroid(x=xandyList[0],y=xandyList[1],\
                source=MEDIUM_IMAGE,width=(2*MEDIUM_RADIUS),\
                    height=(2*MEDIUM_RADIUS),size=MEDIUM_ASTEROID,\
                        direction=[collisionVector.x, collisionVector.y]))
            center = MEDIUM_RADIUS*resultantVector1
            xandyList = [oldX+center.x, oldY+center.y]
            self._asteroids.append(Asteroid(x=xandyList[0],y=xandyList[1],\
                source=MEDIUM_IMAGE,width=(2*MEDIUM_RADIUS),\
                    height=(2*MEDIUM_RADIUS),size=MEDIUM_ASTEROID,\
                        direction=[resultantVector1.x, resultantVector1.y]))  
            center = MEDIUM_RADIUS*resultantVector2
            xandyList = [oldX+center.x, oldY+center.y]
            self._asteroids.append(Asteroid(x=xandyList[0],y=xandyList[1],\
                source=MEDIUM_IMAGE,width=(2*MEDIUM_RADIUS),\
                    height=(2*MEDIUM_RADIUS),size=MEDIUM_ASTEROID,\
                        direction=[resultantVector2.x, resultantVector2.y]))   

    def _splitMediumAsteroid(self, mediumDeleted, oldX, oldY,\
        collisionVector, resultantVector1, resultantVector2):
        """
        Splits a medium asteroid into three small asteroids.

        Parameter mediumDeleted: the amount of medium asteroids that need to be 
        deleted. This parameter is also used to determine how many medium 
        asteroids need to be broken up into small asteroids.
        Precondition: mediumDeleted is an int >= 0.

        Parameter oldx: the x position of the colliding Asteroid's center.
        Precondition: oldX is an int or float.

        Parameter oldY: the y position of the colliding Asteroid's center.
        Precondition: oldY is an int or float.

        Parameter collisionVector: the vector created from 
        the collision of a bullet and an asteroid
        or from the collision of a ship and an asteroid.
        Precondition: collisionVector is a Vector2 object or None.

        Parameter resultantVector1: resultantVector1 is collisionVector .
        but rotated left 120 degrees. 
        precondition: resultantVector1 is a Vector2 object.

        Parameter resultantVector2: resultantVector1 is collisionVector 
        but rotated right 120 degrees. 
        precondition: resultantVector2 is a Vector2 object.
        """
        for i in range(mediumDeleted):
            center = SMALL_RADIUS*collisionVector
            xandyList = [oldX+center.x, oldY+center.y]
            self._asteroids.append(Asteroid(x=xandyList[0],y=xandyList[1],\
                source=SMALL_IMAGE,width=(2*SMALL_RADIUS),\
                    height=(2*SMALL_RADIUS),size=SMALL_ASTEROID,\
                        direction=[collisionVector.x, collisionVector.y]))
            center = SMALL_RADIUS*resultantVector1
            xandyList = [oldX+center.x, oldY+center.y]
            self._asteroids.append(Asteroid(x=xandyList[0],y=xandyList[1],\
                source=SMALL_IMAGE,width=(2*SMALL_RADIUS),\
                    height=(2*SMALL_RADIUS),size=SMALL_ASTEROID,\
                        direction=[resultantVector1.x, resultantVector1.y]))  
            center = SMALL_RADIUS*resultantVector2
            xandyList = [oldX+center.x, oldY+center.y]
            self._asteroids.append(Asteroid(x=xandyList[0],y=xandyList[1],\
                source=SMALL_IMAGE,width=(2*SMALL_RADIUS),\
                    height=(2*SMALL_RADIUS),size=SMALL_ASTEROID,\
                        direction=[resultantVector2.x, resultantVector2.y]))  