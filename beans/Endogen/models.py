from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)

# Numpy is a mathematical python library which is used from more complex calculations. When we want to call it we can use np.
import numpy as np

author = 'Moritz Sommerlad'

doc = """
This is the first out of three experiments for the Seminar on Experimental Economics in the WS 2020 at the AWI Heidelberg
"""


class Constants(BaseConstants):

    # Here we define the different values that are valid in every form of the game.

    name_in_url = 'Endogen'#The name can be set to whatever you want it to be. It will show in the URL.
    players_per_group = 3 #Players per group can be set here. In our case the we play a one-shot three person game. You can change this to any INT. Just make sure you change it in the settings tab as well.
    num_rounds = 1 # You can play more than one round, but in our case we play one.
    pool = 30 #This defines how big the pool is. You can use any INT or String here
    efficiency_factor = 2 # This is a INT that indicates how the resource increases the leftover points. You can use any INT or String here
    tipping_point = 15 # This is the value that acts as a threshhold. If less than those points remain the pool collapses. You can insert any float between 0 and 1.
    max = int(np.floor(pool / players_per_group)) #The max value is calculated by the point available and the number of players.
    # np.floor rounds it down and int converts it to an integer. The last step is not necessary, but it looks better.

class Subsession(BaseSubsession): # Ideally you do not need to change anything here.

    # Here we define the different treatments that are available in the different subversions.

    # This is done by having a Boolean (either TRUE or FALSE) for the Treatment.
    treatment = models.BooleanField()

    # We then create a session. Here we need to specify if the session should have any special properties. In this case we choose that we
    #want a treatment based on our Boolean in line 35. If we wanted another treatment, like different tipping points, we need to add a bool here.
    def creating_session(self):
        self.treatment = self.session.config.get('treatment')



class Group(BaseGroup):

    #The group-level is used to define values that are the same for every player in the group and to aggregate over the players.

    #We check if the pool breaks down by calling the tipping point and calculating the reamining points. 
    # If the tipping point is higher than the remaining points, breakdown will be TRUE.
    # We set this breakdown as a function that can be called during the experiment.
    # Since we only evaluate it if we are playing the treatment, we condition it by an if statement.

    breakdown = models.BooleanField(initial=False)

    def set_breakdown(self):
        if self.subsession.treatment == 1:
            self.breakdown = Constants.tipping_point > (Constants.pool - sum([p.take for p in self.get_players()]))


    #We have to define empty fields which we want to have in our group level. They will get updated later in the function down below.
    # total_points_left is the number of points that do not get take.
    # resource share is the share each player receives from the resource.
    total_points_left = models.IntegerField()
    resource_share = models.FloatField()


    #with def you can define a function that can be called at a later during the experiment.
    # If we want the player we need to use player. or for p in self get._players()
    def set_payoffs(self):

        # to calculate the points left we need the sum of all points the players took.
        # This is done with sum([p.take for p in self.get_players()]). Take is defined in the player class.
        self.total_points_left = Constants.pool - sum([p.take for p in self.get_players()])

        # the resource_share is the amount every player gets back from the pool.
        # to calculate the resource_share we need to know how much remained in the pool , multiply it by the factor and devide it by the number of players.
        # we need to add an if statement since our resource_share is 0 if the pool breaks down. Remember it can only break down if we are in the treatment version.
        if self.breakdown == True:
            self.resource_share = 0
        else:
            #Here we use np.round(number, number of decimals) to aviod getting a number like 13,33333333333
            self.resource_share = np.round(self.total_points_left * Constants.efficiency_factor / Constants.players_per_group, 1)

         # The payoff for each player is determined by the the amount he took and what his share of the common resource is.
         # We do not need to check for the treatment or anything else, since this is already defined in the calculation of the var resource_share

        for p in self.get_players():
            p.payoff = sum([+ p.take,
                            + self.resource_share,
                            ])


class Player(BasePlayer):

    # The Player-level is used to define var on the player level. In otree this means everything that involves a players direct choice.
    # In our case it is the amount he takes.

    # the max a player can take is the third of the pool, rounded down. e.g. pool = 40 --> 40/3 = 13,33. Since we only want round numbers,
    # we take the floor (13,0) and convert it  This can be avoided by picking a number that is divisible by 3. To round down we use the numpy (np) function floor.
    #Additionally we give the field a label which is then displayed on our html page without any further action.
    take = models.PositiveIntegerField(max = int(np.floor(Constants.pool/Constants.players_per_group)), label="How many points do you want to take ?")
