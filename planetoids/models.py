"""
Models module for Planetoids

This module contains the model classes for the Planetoids game. Anything that you
interact with on the screen is model: the ship, the bullets, and the planetoids.

We need models for these objects because they contain information beyond the simple
shapes like GImage and GEllipse. In particular, ALL of these classes need a velocity
representing their movement direction and speed (and hence they all need an additional
attribute representing this fact). But for the most part, that is all they need. You
will only need more complex models if you are adding advanced features like scoring.

You are free to add even more models to this module. You may wish to do this when you
add new features to your game, such as power-ups. If you are unsure about whether to
make a new class or not, please ask on Ed Discussions.

Aaron Baruch Ilan Klimberg 
12/7/2022
"""
from consts import *
from game2d import *
from introcs import *
import math

# PRIMARY RULE: Models are not allowed to access anything in any module other than
# consts.py. If you need extra information from Gameplay, then it should be a 
# parameter in your method, and Wave should pass it as a argument when it calls 
# the method.

# START REMOVE
# HELPER FUNCTION FOR MATH CONVERSION


def degToRad(deg):
    """
    Returns the radian value for the given number of degrees.
    
    Parameter deg: The degrees to convert.
    Precondition: deg is a float.
    """
    return math.pi*deg/180


class Bullet(GEllipse):
    """
    A class representing a bullet from the ship
    
    Bullets are typically just white circles (ellipses). The size of the 
    bullet is determined by constants in consts.py. However, we MUST 
    subclass GEllipse, because we need to add an extra attribute for the 
    velocity of the bullet.
    
    The class Wave will need to look at this velocity, so you will need 
    getters for the velocity components. However, it is possible to write 
    this assignment with no setters for the velocities. That is because the 
    velocity is fixed and cannot change once the bolt is fired.
    
    In addition to the getters, you need to write the __init__ method to set 
    the starting velocity. This __init__ method will need to call the __init__ 
    from GEllipse as a helper. This init will need a parameter to set the 
    direction of the velocity.
    
    You also want to create a method to update the bolt. You update the 
    bolt by adding the velocity to the position. While it is okay to add a 
    method to detect collisions in this class, you may find it easier to process
    collisions in wave.py.
    """
    # LIST ANY ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
    # Attribute _velocity: the direction and speed (velocity) the bullet 
    # is traveling.
    # Invariant: _velocity is a Vector2 object.
    
    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)

    def getVelocity(self):
        """
        Returns the bullet's velocity.
        """
        return self._velocity

    # INITIALIZER TO SET THE POSITION AND VELOCITY
    def __init__(self, x, y, width, height, fillcolor, facing): 
        """
        Initializes a new Bullet object with the given GEllipse attributes, and
        sets velocity of the bullet based on the ship's facing.
        
        Parameter x: The horizontal coordinate of the ship's center.
        Precondition: x is an int or float.

        Parameter y: The vertical coordinate of the ship's center.
        Precondition: y is an int or float.

        Parameter width: The width of the ship.
        Precondition: width must be an int or float greater than 0.

        Parameter height: The height of the image.
        Precondition: height must be an int or float greater than 0.

        Parameter fillcolor: fillcolor is used to color the background
        or, in the case of solid shapes, the shape interior.
        If there is no value (e.g. the fillcolor is None), 
        this shape willl have no interior.

        The default representation of color in GObject is a 4-element list 
        of floats between 0 and 1 (representing r, g, b, and a). As with the 
        Turtle, you may also assign color an RGB or HSV object from colormodel, 
        or a string with a valid color name. 
        If you chose either of these alternate representations 
        (a string or an object from colormodel), 
        Python will automatically convert the result into a 4-element list.

        Precondition: fillcolor must be None or a 4-element 
        list of floats between 0 and 1.

        Parameter facing: the ship's facing, converted to a unit vector.
        Precondition: facing is a Vector2 object.
        """
        super().__init__(x=x,y=y,width=width,height=height,fillcolor=fillcolor)
        self._velocity = facing * BULLET_SPEED
    
    # ADDITIONAL METHODS (MOVEMENT, COLLISIONS, ETC)
    def move(self):
        """
        Moves the bullets by updating the position of the bullets based
        on velocity.
        """
        self.x += self._velocity.x
        self.y += self._velocity.y

    def isOut(self):
        """
        Returns True if the bullet x and y position are outside of the 
        DEAD_ZONE, otherwise returns False.
        """
        if self.x > GAME_WIDTH+DEAD_ZONE:
            return True
        elif self.x < -DEAD_ZONE:
            return True
        elif self.y > GAME_HEIGHT+DEAD_ZONE:
            return True
        elif self.y < -DEAD_ZONE:
            return True
        else:
            return False


class Ship(GImage):
    """
    A class to represent the game ship.
    
    This ship is represented by an image. The size of the ship is determined by 
    constants in consts.py. However, we MUST subclass GEllipse, because we need 
    to add an extra attribute for the velocity of the ship, as well as the facing 
    vecotr (not the same) thing.
    
    The class Wave will need to access these two values, so you will need getters 
    for them. But per the instructions,these values are changed indirectly by 
    applying thrust or turning the ship. That means you won't want setters for 
    these attributes, but you will want methods to apply thrust or turn the ship.
    
    This class needs an __init__ method to set the position and initial facing 
    angle. This information is provided by the wave JSON file. Ships should 
    start with a shield enabled.
    
    Finally, you want a method to update the ship. When you update the ship, 
    you apply the velocity to the position. While it is okay to add a method 
    to detect collisions in this class, you may find it easier to process 
    collisions in wave.py.
    """
    # LIST ANY ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
    # Attribute _velocity: The direction and speed (velocity) the ship 
    # is travelling
    # Invariant: _velocity is a Vector2 object
    #
    # Attribute _facing: The direction the ship is facing
    # Invariant: _facing is a Vector2 object
    
    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)
    def getVelocity(self):
        """
        Returns the ship's velocity.
        """
        return self._velocity

    def getFacing(self):
        """
        Returns the ship's facing.
        """
        return self._facing
    
    # INITIALIZER TO CREATE A NEW SHIP
    def __init__(self, x, y, angle, source, width, height):
        """
        Initializes a new Ship object with the given GImage attributes, and 
        sets the initial velocity and facing vectors of the ship.
        
        Parameter x: The horizontal coordinate of the ship's center.
        Precondition: x is an int or float.

        Parameter y: The vertical coordinate of the ship's center.
        Precondition: y is an int or float.

        Parameter angle: The angle of roation about the center.
        The angle is measured in degrees (not radians) counter-clockwise.
        Precondition: angle is an int or float.

        Parameter source: The source file for the image of the ship.
        Precondition: source must be a string refering to a valid file.

        Parameter width: The width of the ship.
        Precondition: width must be an int or float greater than 0.

        Parameter height: The height of the image.
        Precondition: height must be an int or float greater than 0.
        """
        super().__init__(x=x,y=y,angle=angle,source=source,width=width,\
            height=height)
        self._velocity = introcs.Vector2(0,0)
        rad = degToRad(self.angle)
        self._facing = introcs.Vector2(x=math.cos(rad),y=math.sin(rad))
    
    # ADDITIONAL METHODS (MOVEMENT, COLLISIONS, ETC)
    def turn(self, angle):
        """
        Updates the angle and facing of the ship as it turns.

        Parameter angle: the angle of the ship's facing in degrees.
        Precondition: angle must be a float.
        """
        rad = degToRad(angle)
        self._facing = introcs.Vector2(x=math.cos(rad),y=math.sin(rad))

    def thrust(self, input):
        """
        Updates the velocity and position of the ship due to impulse of 
        the thrust.

        Parameter input: the user input, used to control the ship and 
        change state.
        Precondition: input is an instance of GInput.
        """
        impulse = self._facing * SHIP_IMPULSE
        if input.is_key_down('up'):
            self._velocity += impulse
            if self._velocity.length() > SHIP_MAX_SPEED:
                self._velocity = self._velocity.normal()
                self._velocity *= SHIP_MAX_SPEED
        self.x += self._velocity.x
        self.y += self._velocity.y 


class Asteroid(GImage):
    """
    A class to represent a single asteroid.
    
    Asteroids are typically are represented by images. Asteroids come in three 
    different sizes (SMALL_ASTEROID, MEDIUM_ASTEROID, and LARGE_ASTEROID) that 
    determine the choice of image and asteroid radius. We MUST subclass GImage, 
    because we need extra attributes for both the size and the velocity of 
    the asteroid.
    
    The class Wave will need to look at the size and velocity, so you will need 
    getters for them.  However, it is possible to write this assignment with no 
    setters for either of these. That is because they are fixed and cannot change 
    when the planetoid is created. 
    
    In addition to the getters, you need to write the __init__ method to set 
    the size and starting velocity. Note that the SPEED of an asteroid is 
    defined in const.py, so the only thing that differs is the velocity direction.
    
    You also want to create a method to update the asteroid. You update the 
    asteroid by adding the velocity to the position. While it is okay to add a 
    method to detect collisions in this class, you may find it easier to 
    process collisions in wave.py.
    """
    # LIST ANY ATTRIBUTES (AND THEIR INVARIANTS) HERE IF NECESSARY
    # Attribute _size: the size of the asteroid.
    # Invariant: _size is a string representing the size name of the asteroid;
    # either 'small', 'medium', or 'large'.
    #
    # Attribute _velocity: The direction and speed (velocity) 
    # the asteroid is travelling.
    # Invariant: _velocity is a Vector2 object.
    #
    # Attribute _delete: indicates whether the Asteroid should be 
    # deleted after collision.
    # Invariant: _delete is a bool True or False.
    
    # GETTERS AND SETTERS (ONLY ADD IF YOU NEED THEM)

    def getSize(self):
        """
        Returns the asteroid's size.
        """
        return self._size

    def getDel(self):
        """
        Returns _delete attribute that indicates whether the asteroid should
        be deleted.
        """
        return self._delete
       
    def setDel(self, value):
        """
        Sets _delete attribute.

        Paremeter value: Whether the asteroid should be deleted or not.
        precondition: value is a boolean True or False
        """
        self._delete = value
    
    # INITIALIZER TO CREATE A NEW ASTEROID
    def __init__(self, x, y, source,width, height, size, \
        direction, delete=False):
        """
        Initializes a new Asteroid object with the given GImage attributes, and
        sets the size and velocity of the asteroid based on the "size" and 
        "direction" keys.
        
        Parameter x: The horizontal coordinate of the ship's center.
        Precondition: x is an int or float.

        Parameter y: The vertical coordinate of the ship's center.
        Precondition: y is an int or float.

        Parameter source: The source file for the image of the ship.
        Precondition: source must be a string refering to a valid file.

        Parameter width: The width of the ship.
        Precondition: width must be an int or float greater than 0.

        Parameter height: The height of the image.
        Precondition: height must be an int or float greater than 0.

        Parameter size: the size of the asteroid.
        Precondition: size is a string representing the size name of the 
        asteroid; either 'small', 'medium', or 'large'.

        Parameter direction: The velocity direction of the asteroid.
        represented as a list of the x and y attributes of a Vector2 object.
        Precondition: direction is a two-element list of ints or floats.

        Parameter delete: Delete is a boolean stating if we need
        to delete the asteroid.
        Precondition: delete is a boolean.
        """
        super().__init__(x=x,y=y,source=source,width=width,height=height)
        self._size = size
        vector = introcs.Vector2(x=direction[0],y=direction[1])
        if direction == [0,0]:
            self._velocity = introcs.Vector2(0,0)
        elif size == SMALL_ASTEROID:
            self._velocity = vector.normal()*SMALL_SPEED
        elif size == MEDIUM_ASTEROID:
            self._velocity = vector.normal()*MEDIUM_SPEED
        elif size == LARGE_ASTEROID:
            self._velocity = vector.normal()*LARGE_SPEED
        self.setDel(delete)
    
    # ADDITIONAL METHODS (MOVEMENT, COLLISIONS, ETC)
    def move(self):
        """
        Moves the asteroids by updating the position of the asteroid based
        on velocity.
        """
        self.x += self._velocity.x
        self.y += self._velocity.y 

# IF YOU NEED ADDITIONAL MODEL CLASSES, THEY GO HERE