import onslaught_game as OG
import math


class AssassinSpells:
    def poisonShuriken(self):
        """ Throw a poison-tipped shuriken in the direction of your mouse that deals 50 damage + 110% of attack power to any enemy hit and slows them by 30% for 3 seconds. """
        #pos = pag.position() #queryMousePosition()
        #print(pos)
        x = OG.mouse_x
        y = OG.mouse_y
        
        shuriken = OG.SpellSprite("images/shuriken.png", 0.5)
        shuriken_speed = 15

        # Position the bullet at the player's current location
        start_x = OG.onslaught.player.center_x
        start_y = OG.onslaught.player.center_y
        shuriken.center_x = start_x
        shuriken.center_y = start_y

        # Get from the mouse the destination location for the bullet
        # IMPORTANT! If you have a scrolling screen, you will also need
        # to add in self.view_bottom and self.view_left.
        dest_x = x
        dest_y = y

        # Do math to calculate how to get the bullet to the destination.
        # Calculation the angle in radians between the start points
        # and end points. This is the angle the bullet will travel.
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        # Angle the bullet sprite so it doesn't look like it is flying
        # sideways.
        shuriken.angle = math.degrees(angle)
        #print(f"Bullet angle: {basic_attack.angle:.2f}")

        # Taking into account the angle, calculate our change_x
        # and change_y. Velocity is how fast the bullet travels.
        shuriken.change_x = math.cos(angle) * shuriken_speed
        shuriken.change_y = math.sin(angle) * shuriken_speed

        # Add the bullet to the appropriate lists
        OG.onslaught.basic_attack_list.append(shuriken)
        OG.onslaught.ll_sprites.append(shuriken)

    def assassinate(self):
        """ Step through the shadows to an enemy target and stab them in the back for 50 damage + 110% of attack power. Always a critical hit. Must have mouse cursor on an enemy to perform. """
        pass

    def vanish(self):
        """ Vanish into the darkness and become hidden from your enemies for 3 seconds. """
        pass

    def masterOfDeception(self):
        """ You are a master of deception. Summon 3 clones of your self that will act as you do, mimicking your actions (without damage) and confusing your enemies. """
        pass

class MageSpells:
    def eruption(self):
        """ Explode, shooting fiery comets from all around you that burn any enemy hit for 50 damage + 110% of spell power. """
        pass

    def teleport(self):
        """ Teleport to your current mouse location.  (OR, Teleport to a location clicked on). """
        pass

    def freezingNova(self):
        """ Freeze all nearby enemies in their place for 3 seconds and deal 25 damage + 80% of spell power. """
        pass

    def glacialComet(self):
        """ Send a glacial comet soaring toward the direction of your mouse that deals 100 + 150% of spell power to any enemy hit, slowing them by 70% for 3 seconds. """
        pass

class VoidStalkerSpells:
    def voidTippedBlade(self):
        """ Your next basic attack deals 50 damage + 90% of attack power and 20% of spell power.  If the target is a player, the player will have 10% of their mana drained. """
        pass

    def shadowGrip(self):
        """ Shoot a bolt of shadow in the direction of your mouse. If it hits an enemy, deal 25 damage + 50% of attack power and grip them through the shadows to your current location, immobilizing them for 1 second. """
        pass

    def voidNova(self):
        """ Explode with the power of the void, sending out void bolts in all directions dealing 50 damage + 60% of attack power and 20% of spell power to all enemies hit.  If the target is a player,the player will have 10% of their mana drained. """
        pass

    def enterTheVoid(self):
        """ Enter the void, stepping into another dimension and becoming unseen by enemies for 8 seconds. While active, you are slowed, but you can attack your enemies undetected and unseen with 25% increased attack power. At the
        end of the duration, you will exit the void from where you entered, becoming visible again. Area effect spells and abilities can still hit you in the void. """
        pass