from pickletools import read_bytes1
from random import random

import sc2
from sc2 import BotAI, Race
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.upgrade_id import UpgradeId
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2
from sc2.player import Bot, Computer
from sc2.constants import *


class CompetitiveBot(BotAI):
    NAME: str = "CompetitiveBot"
    """This bot's name"""
    RACE: Race = Race.Zerg
    """This bot's Starcraft 2 race.
    Options are:
        Race.Terran
        Race.Zerg
        Race.Protoss
        Race.Random
    """

    def __init__(self):

        sc2.BotAI.__init__(self)
        self.distance_calculation_method = 3
        self.ITERATIONS_PER_MINUTE = 165
        
    #ravager bot testing - bits-of-code eschamp studio credits
        
    def select_target(self):
        targets = self.enemy_structures
        if targets:
            return targets.random.position, True

        targets = self.enemy_units
        if targets:
            return targets.random.position, True

        if self.units and min([u.position.distance_to(self.enemy_start_locations[0]) for u in self.units]) < 5:
            return self.enemy_start_locations[0].position, False

       # return self.mineral_field.random.position, False
    
    

    
    async def on_start(self):
        print("Game started")
        # Do things here before the game starts
       

    async def on_step(self, iteration):
        
        #more ravager code frankensteining in this chunk of 8 lines below
        
        #ravagers = self.units(UnitTypeId.RAVAGER)
        #if ravagers:
         # target, target_is_enemy_unit = self.select_target()
          
          
          
          #for ravager in ravagers:
           # if target_is_enemy_unit and (ravager.is_idle or ravager.is_moving):
            #  self.do(ravager.attack(target))
            #elif ravager.is_idle:
             #  self.do(ravager.move(target))
              
              

        
        self.iteration = iteration
        #below two lines stolen from code - sc2 python examples https://eschamp.com/guides/how-to-quickly-start-with-a-terran-bot-in-python/ example script in sc2 folder - zerg - hydralisk push
        larvae: Units = self.larva
        forces: Units = self.units.of_type({UnitTypeId.RAVAGER, UnitTypeId.ROACH})
        # Populate this function with whatever your bot should do!
        await self.distribute_workers()
        #my contribution, start game - worker extractor trick
        await self.start_game()
        await self.second_extractor()
        await self.cancel_extractor()
        await self.build_workers(iteration)
        await self.build_overlords(iteration)
        await self.move_overlords(iteration)
        await self.build_spawning_pool()
        await self.build_gas()
        await self.build_roach_warren()
        await self.train_roaches(iteration)
        await self.train_zerglings(iteration)
        await self.move_forces(iteration)
        await self.train_queen()
        await self.inject_larva(iteration)
        await self.morph_ravagers(iteration)
        await self.saturate_gas()
        await self.micro(iteration)
        await self.cast_corrosive_bile()
        
        pass
    
    
    async def start_game(self):
        overlords = self.units.of_type({UnitTypeId.OVERLORD})
        hatchery = self.townhalls.first
        if overlords.amount < 2 and self.supply_workers == 13 and self.can_afford(UnitTypeId.EXTRACTOR) and self.workers.amount > 12 and overlords.closer_than(24, hatchery):
            if self.already_pending(UnitTypeId.EXTRACTOR) < 1:
             for hatchery in self.townhalls.ready:
                vgs = self.vespene_geyser.closer_than(15, hatchery)
                for vg in vgs:
                    if not self.can_afford(UnitTypeId.EXTRACTOR):
                        break
                    worker = self.select_build_worker(vg.position)
                    if worker is None:
                        break
                    if not self.gas_buildings or not self.gas_buildings.closer_than(2, vg):
                        worker.build(UnitTypeId.EXTRACTOR, vg)
                        
    #clone of upper clas, but to do second (trick, accumulating by one extra worker - to making extractor build timing work)                    
    async def second_extractor(self):
        overlords = self.units.of_type({UnitTypeId.OVERLORD})
        hatchery = self.townhalls.first
        if overlords.amount < 2 and self.can_afford(UnitTypeId.EXTRACTOR) and self.already_pending(UnitTypeId.OVERLORD) == 0 and self.workers.amount > 12 and not overlords.closer_than(20, hatchery) and overlords.closer_than(24, hatchery):
            if self.already_pending(UnitTypeId.EXTRACTOR) < 2: 
            # and self.iteration >= 200:
             for hatchery in self.townhalls.ready:
                vgs = self.vespene_geyser.closer_than(15, hatchery)
                for vg in vgs:
                    if not self.can_afford(UnitTypeId.EXTRACTOR):
                        break
                    worker = self.select_build_worker(vg.position)
                    if worker is None:
                        break
                    if not self.gas_buildings or not self.gas_buildings.closer_than(2, vg):
                        worker.build(UnitTypeId.EXTRACTOR, vg)
                         
    async def cancel_extractor(self):
         overlords = self.units.of_type({UnitTypeId.OVERLORD})
         ravagers = self.units.of_type({UnitTypeId.DRONE})
         eggs = self.units.of_type({UnitTypeId.EGG})
         if overlords.amount < 2 and self.already_pending(UnitTypeId.EXTRACTOR) > 1 and ravagers.amount > 11:
            if eggs.amount > 1:
             for extractor in self.structures(UnitTypeId.EXTRACTOR): 
                 extractor(AbilityId.CANCEL)     
    
    #below is not my code! https://github.com/joelibaceta/zerg-infestation-strategy/blob/master/zerg_bot.py
    #async def explore_the_map(self):
        #"""Mantener Overlords explorando el mapa continuamente de base en base"""

     #   scout_locations = [location for location in self.expansion_locations_list if
      #                     location not in self.enemy_start_locations]

       # for overlord in self.units.of_type({UnitTypeId.OVERLORD}).idle:
        #     self.do(overlord.move(random.choice(scout_locations)))
    
    async def build_workers(self, iteration):
        larvae: Units = self.larva
        ravagers = self.units.of_type({UnitTypeId.DRONE})
        if larvae and self.can_afford(UnitTypeId.DRONE) and iteration < 240:
            self.train(UnitTypeId.DRONE) 
            
    async def build_overlords(self, iteration):
        
        larvae: Units = self.larva
       # forces: Units = self.units.of_type({UnitTypeId.RAVAGER, UnitTypeId.ROACH})
        #overlords: Units = self.units.of_type({UnitTypeId.OVERLORD})
        hatchery = self.townhalls.first
        #pos  = hatchery.position.towards(self.enemy_start_locations[0], 10)
        spawning_pool = self.structures(UnitTypeId.SPAWNINGPOOL)
            
        if self.supply_left < 2 and larvae and self.can_afford(UnitTypeId.OVERLORD) and self.already_pending(UnitTypeId.OVERLORD) == 0:
            larvae.random.train(UnitTypeId.OVERLORD)
            return
        
        if self.supply_left < 6 and larvae and self.can_afford(UnitTypeId.OVERLORD) and self.already_pending(UnitTypeId.OVERLORD) == 0 and self.already_pending(UnitTypeId.QUEEN) == 1:
            larvae.random.train(UnitTypeId.OVERLORD)
            return
        if self.supply_left < 6 and larvae and self.can_afford(UnitTypeId.OVERLORD) and self.already_pending(UnitTypeId.OVERLORD) == 0 and iteration > 330 and iteration < 500:
            larvae.random.train(UnitTypeId.OVERLORD)
            return
        
        if self.supply_left < 2 and larvae and self.can_afford(UnitTypeId.OVERLORD) and self.already_pending(UnitTypeId.OVERLORD) == 0 and iteration > 500:
            larvae.random.train(UnitTypeId.OVERLORD)
            return
            
    async def move_overlords(self, iteration): 
        
      overlords: Units = self.units.of_type({UnitTypeId.OVERLORD})
      
      ravagers = self.units.of_type({UnitTypeId.RAVAGER, UnitTypeId.ROACH})
    
      
      hatchery = self.townhalls.first
      enemy_loc = self.enemy_start_locations[0]
      pos1 = hatchery.position.towards(self.enemy_start_locations[0],48)
      pos2 = self.game_info.map_center
     # pos3 = sc2.position.Point2((20.20, 20.20))
      #pos4 = sc2.position.Point2((40.20, 20.20))
      #pos5 = sc2.position.Point2((40.20, 40.20))
      #pos6 = sc2.position.Point2((40.20, 40.40))
      
      pos1offset = pos1.offset((20.0, 0.10))
      pos2offset = pos1.offset((-20.0, 0.10))
      pos3offset = pos1.offset((40.0, 0.10))
      pos4offset = pos1.offset((-40.0,0.10))
            #? experimental code under this, just one line
        #await overlords.attack(pos)  
      
    
        
                   
                 
      if self.units(UnitTypeId.OVERLORD).amount >= 1:
              
          
          for unit in overlords.idle:
            dummies = overlords.closer_than(15, hatchery)
             # smarties = overlords.further_than(27, hatchery) and overlords.closer_than(40, hatchery)
            outlaws = overlords.further_than(30, hatchery)
            #  pos3ers = overlords.closer_than(2, pos4)
            #  pos4ers = overlords.closer_than(2, pos5)
            #  pos5ers = overlords.closer_than(2, pos6)
              
              #testers = overlords.closer_than(5, hatchery)
              
             
              
            for dummy in dummies: 
                if self.supply_cap < 16 and iteration < 400:  
                  dummy.move(pos1)
                elif self.supply_cap >15 and self.supply_cap < 23 and iteration < 400:
                  dummy.move(pos1offset)
                elif self.supply_cap >22 and self.supply_cap < 31 and iteration < 400:
                  dummy.move(pos2offset)
                elif self.supply_cap >30 and self.supply_cap < 39 and iteration < 400:
                  dummy.move(pos3offset)
                elif self.supply_cap >38 and self.supply_cap < 47 and iteration < 400:
                  dummy.move(pos4offset)   
                  
                else:
                  dummy.move(enemy_loc)
                  
            for outlaw in outlaws:
                if iteration > 400:
                   outlaw.move(enemy_loc)
                  
              #for smarty in smarties:
               #   smarty.move(pos3)
              #for outlaw in outlaws:
               #   outlaw.move(pos4)
             # for pos3er in pos3ers:
                #  pos3er.move(pos5)
             # for pos4er in pos4ers:
                 # pos4er.move(pos6)
             # for pos5er in pos5ers:
                  #pos5er.move(pos1)
             # for tester in testers:
                  #tester.move(pos1offset)
                  
      

    async def build_spawning_pool(self):
        if (
           #( self.structures(UnitTypeId.PYLON).ready)  -- changing this to line below and pray it works, its not terribly important to my goal of the build order
            self.can_afford(UnitTypeId.SPAWNINGPOOL)
            and not self.structures(UnitTypeId.SPAWNINGPOOL)
           ): 
            my_hatch = self.structures(UnitTypeId.HATCHERY).first
            await self.build(UnitTypeId.SPAWNINGPOOL, near = my_hatch.position.towards(self.game_info.map_center, 5))

    async def build_gas(self):
         #? experimental code under this, kinda, confident that the below line will work correctly
        overlords: Units = self.units.of_type({UnitTypeId.OVERLORD})
        if self.units(UnitTypeId.DRONE).amount > 14 and self.already_pending(UnitTypeId.EXTRACTOR) < 2 and overlords.amount > 1:
            for hatchery in self.townhalls.ready:
                vgs = self.vespene_geyser.closer_than(15, hatchery)
                for vg in vgs:
                    if not self.can_afford(UnitTypeId.EXTRACTOR):
                        break
                    worker = self.select_build_worker(vg.position)
                    if worker is None:
                        break
                    if not self.gas_buildings or not self.gas_buildings.closer_than(1, vg):
                        worker.build(UnitTypeId.EXTRACTOR, vg)
                        #worker.stop(queue=True)
                        
    async def saturate_gas(self):
        # Saturate gas
        for a in self.gas_buildings:
            if a.assigned_harvesters < a.ideal_harvesters:
                w: Units = self.workers.closer_than(10, a)
                if w:
                    w.random.gather(a)
                        
    async def build_roach_warren(self):
        if self.structures(UnitTypeId.SPAWNINGPOOL).ready:
            hatchery = self.structures(UnitTypeId.HATCHERY).first
            if self.structures(UnitTypeId.SPAWNINGPOOL).ready:
                #if no roach warren, then build one
                if not self.structures(UnitTypeId.ROACHWARREN):
                    if(
                        self.can_afford(UnitTypeId.ROACHWARREN)
                        and self.already_pending(UnitTypeId.ROACHWARREN) == 0
                    ):
                        await self.build(UnitTypeId.ROACHWARREN, near = hatchery.position.towards(self.game_info.map_center, 5))
                        
    async def train_roaches(self, iteration):
        larvae: Units = self.larva
        if self.structures(UnitTypeId.ROACHWARREN).ready:
                if larvae and self.can_afford(UnitTypeId.ROACH) and iteration < 484 and self.supply_left > 3:
                 
                        self.train(UnitTypeId.ROACH)
                        
    async def train_zerglings(self, iteration):
        larvae: Units = self.larva
        if self.structures(UnitTypeId.SPAWNINGPOOL).ready:
                if larvae and self.can_afford(UnitTypeId.ZERGLING) and self.already_pending(UnitTypeId.ZERGLING) == 0 and self.supply_army < 3 and self.already_pending(UnitTypeId.QUEEN) == 1:
                 
                        self.train(UnitTypeId.ZERGLING)
            
    async def move_forces(self, iteration):
        hatchery = self.townhalls.first
        overlords: Units = self.units.of_type({UnitTypeId.OVERLORD})
        
        zerglings: Units = self.units.of_type({UnitTypeId.ZERGLING})
        
        pos = hatchery.position.towards(self.enemy_start_locations[0],30)
        pos2 = hatchery.position.towards(self.enemy_start_locations[0],70)
        pos3 = hatchery.position.towards(self.enemy_start_locations[0],90)
        
        ravagers: Units = self.units.of_type({UnitTypeId.RAVAGER})
        drones: Units = self.units.of_type({UnitTypeId.DRONE})
        
        forces = self.units.of_type({UnitTypeId.ROACH, UnitTypeId.RAVAGER}).ready.idle
        for force in forces:
            #if(self.supply_army < 21):
        
             #force.attack(pos)
             if iteration > 420 and iteration <= 460:
              force.attack(pos) 

             if iteration > 480 and iteration <= 570:
              force.attack(pos2)
             
             if iteration > 570:
              force.attack(pos3)
           
           #attack with drones
        if iteration > 552:
           for drone in drones:
                if not self.gas_buildings.closer_than(5, drone):
                
                    drone.attack(self.enemy_start_locations[0])
                    
            #attack with drones (gas drones lastly)
        if iteration > 588:
           for drone in drones:
                
                    drone.attack(self.enemy_start_locations[0])           
       # if self.supply_army > 22:
          #  for force in forces:
           #     force.attack(self.enemy_start_locations[0])
        
        #move lings up a bit to defend ramp
        if zerglings.idle:
         for zergling in zerglings:
                
                    zergling.attack (hatchery.position.towards(self.enemy_start_locations[0],10)) 
                               
    async def morph_ravagers(self, iteration):
        hatchery = self.townhalls.first
        roaches: Units = self.units.of_type({UnitTypeId.ROACH}) 
        
        if self.can_afford(UnitTypeId.RAVAGER):   
            
            if iteration > 516:
                for roach in roaches:  
                        vgs = self.units(UnitTypeId.ROACH).closer_than(16, hatchery)
                        for vg in vgs:
                         vg(AbilityId.MORPHTORAVAGER_RAVAGER)
                         
            if iteration > 530:
                for roach in roaches:  
                        vgst = self.units(UnitTypeId.ROACH).closer_than(50, hatchery)
                        for vgt in vgst:
                         vgt(AbilityId.MORPHTORAVAGER_RAVAGER)
                         
            if iteration > 570:
                for roach in roaches:                        
                         roach(AbilityId.MORPHTORAVAGER_RAVAGER)             
            
          
    async def train_queen(self): 
        hatchery = self.townhalls.first
        if self.structures(UnitTypeId.SPAWNINGPOOL).ready:
            if not self.units(UnitTypeId.QUEEN) and hatchery.is_idle:
                if self.can_afford(UnitTypeId.QUEEN):
                   hatchery.train(UnitTypeId.QUEEN)

                
    async def inject_larva(self, iteration):
        hatchery = self.townhalls.first
        for queen in self.units(UnitTypeId.QUEEN).idle:
            # The following checks if the inject ability is in the queen abilitys - basically it checks if we have enough energy and if the ability is off-cooldown
            # abilities = await self.get_available_abilities(queen)
            # if AbilityId.EFFECT_INJECTLARVA in abilities:
            if queen.energy >= 25 and iteration < 400:
                queen(AbilityId.EFFECT_INJECTLARVA, hatchery)
            else:
                queen.attack (hatchery.position.towards(self.enemy_start_locations[0],10))     
                
    async def micro(self, iteration):            
     ravagers = self.units(UnitTypeId.RAVAGER)
     enemy_location = self.enemy_start_locations[0]
     enemy_bunkers = self.enemy_structures({UnitTypeId.BUNKER, UnitTypeId.SPINECRAWLER, UnitTypeId.PHOTONCANNON})
     enemy_tanks = self.enemy_units({UnitTypeId.SIEGETANK, UnitTypeId.IMMORTAL, UnitTypeId.SIEGETANKSIEGED})
     enemies = self.enemy_units.filter(lambda unit: unit.type_id not in {UnitTypeId.LARVA, UnitTypeId.EGG})
     enemy_fighters = enemies.filter(lambda u: u.can_attack) + self.enemy_structures(
			{UnitTypeId.BUNKER, UnitTypeId.SPINECRAWLER, UnitTypeId.PHOTONCANNON})  
      
     if self.structures(UnitTypeId.HATCHERY).ready:
            hatchery = self.structures(UnitTypeId.HATCHERY).closest_to(enemy_location)
            
            for ravager in ravagers:
                
                #enemy_bunkers_in_range = enemy_bunkers.in_attack_range_of(ravager)
                #in_range_enemies = enemy_bunkers.in_attack_range_of(ravager)
                #enemy_tanks_in_range = self.in_attack_range_of(enemy_tanks)
                #in_range_tanks = enemy_tanks.in_attack_range_of(ravager)
                enemy_fighters_in_range = enemy_fighters.in_attack_range_of(ravager)
                
                
                if ravager.weapon_cooldown == 0 and not enemy_bunkers.closer_than(8, ravager) and iteration > 630:
                     ravager.attack(enemy_location)
                elif ravager.weapon_cooldown < 0 and enemy_fighters_in_range:
                    ravager.move(hatchery)
                        
                
    async def build_an_expansion(self):
        """Construir expansiones en los lugares mas adecuados de forma aleatoria"""

        scout_locations = [location for location in self.expansion_locations if
                           location not in self.enemy_start_locations]
        if self.minerals > 400 and self.workers.exists:
            pos = random.choice(scout_locations)
            if await self.can_place(HATCHERY, pos):
                self.spawning_pool_started = True
                await self.do(self.workers.random.build(HATCHERY, pos))

         #burny's shit, doesn't work here       
    async def cast_corrosive_bile(self):
        enemies = self.enemy_units.filter(lambda unit: unit.type_id not in {UnitTypeId.LARVA, UnitTypeId.EGG})
        enemy_fighters = enemies.filter(lambda u: u.can_attack) + self.enemy_structures(
			{UnitTypeId.BUNKER, UnitTypeId.SPINECRAWLER, UnitTypeId.PHOTONCANNON})
        ravagers = self.units(UnitTypeId.RAVAGER)
        drones = self.units(UnitTypeId.DRONE)
        hatchery = self.structures(UnitTypeId.HATCHERY).first
        ravager_bile_range: float = self._game_data.abilities[AbilityId.EFFECT_CORROSIVEBILE.value]._proto.cast_range
        #ravager_bile = self._game_data.abilities[ravager.AbilityId.EFFECT_CORROSIVEBILE]
        
       # enemy_bunkers = self.enemy_structures({UnitTypeId.BUNKER, UnitTypeId.SPINECRAWLER, UnitTypeId.PHOTONCANNON})
        #Me testing things
       # for enemy in enemies:
         #   enemy.calculate_unit_value
            
            
        
        for ravager in ravagers:
            abilities = await self.get_available_abilities(ravager)
            if enemy_fighters:
                closest_enemy = enemy_fighters.closest_to(ravager)
                if closest_enemy:
                    if ravager.distance_to(closest_enemy) < 9 :
                        if self.can_cast(AbilityId.EFFECT_CORROSIVEBILE, closest_enemy.position):
                           here = closest_enemy.position
                           if not drones.closer_than(2,here) and not ravagers.closer_than(2,here):
                             ravager(AbilityId.EFFECT_CORROSIVEBILE, closest_enemy.position)
            
     
            #get range from bunkers
           # and unit.distance_to(r) < reaperGrenadeRange
            
       
      # enemies_can_attack: Units = enemies.filter(lambda unit: unit.can_attack_ground)

        #gonna try mixing ravager code with protoss code
        
        #ravagers = self.units(UnitTypeId.RAVAGER)
       # target = self.enemy_units | self.enemy_structures
       # if ravagers:
            
            #target, target_is_enemy_unit = self.select_target()
           # for ravager in ravagers:
                #frontliner = ravagers.closer_than(20, self.enemy_start_locations[0])
                
              #  abilities = await self.get_available_abilities(ravager) # is bile ready?
                #if target_is_enemy_unit and (ravager.is_idle or ravager.is_moving):
                 #   self.do(ravager.attack(target))
                
                #elif ravager.is_idle:
                 #    self.do(ravager.move(target)) 
                        
            #loc_to_hit = enemies.closest_to(ravager.position)
            #location: Point2 = await self.find_placement(
                    #AbilityId.EFFECT_CORROSIVEBILE, self.enemy_start_locations[0],random.randrange(1, 15))
            #ravager(AbilityId.EFFECT_CORROSIVEBILE, enemies.position)
               # if AbilityId.EFFECT_CORROSIVEBILE in abilities:
                
                  # if self.can_cast(ravager, AbilityId.EFFECT_CORROSIVEBILE):
                        #placement = target.random.position
                        
                        #this works!
                       #ravager(AbilityId.EFFECT_CORROSIVEBILE, self.enemy_start_locations[0])
                       
                       #not this
                      # break
                       
                 
         #   enemyGroundUnits: Units = enemies.filter(
            #    lambda unit: unit.distance_to(ravager) < 6
            #) 
              # Hardcoded attackrange of 6
            #if ravager.weapon_cooldown == 0 and enemyGroundUnits:
             #   enemyGroundUnits: Units = enemyGroundUnits.sorted(lambda x: x.distance_to(ravager))
              #  closestEnemy: Unit = enemyGroundUnits[0]
               # ravager.attack(closestEnemy)
                #continue
                
            #ravager_bile_range: float = self._game_data.abilities[AbilityId.EFFECT_CORROSIVEBILE.value]._proto.cast_range
            #enemyUnitsInBileRange: Units = enemies_can_attack.filter(
             #   lambda unit: not unit.is_structure
              #  and not unit.is_flying
               # and unit.type_id not in {UnitTypeId.LARVA, UnitTypeId.EGG}
                #and unit.distance_to(ravager) < ravager_bile_range)
                
            #if enemyUnitsInBileRange and (ravager.is_attacking or ravager.is_moving):
                 # If AbilityId.KD8CHARGE_KD8CHARGE in abilities, we check that to see if the reaper grenade is off cooldown
                #abilities = await self.get_available_abilities(ravager)
                #enemyUnitsInBileRange = enemyUnitsInBileRange.sorted(
                    #lambda x: x.distance_to(ravager), reverse=True
                #)
                #furthestEnemy: Unit = None
                    
                #for enemy in enemyUnitsInBileRange:
                 #   if await self.can_cast(ravager, AbilityId.EFFECT_CORROSIVEBILE, enemy, cached_abilities_of_unit=abilities):
                  #      furthestEnemy: Unit = enemy
                   #     break
                    #if furthestEnemy:
                     #   ravager(AbilityId.EFFECT_CORROSIVEBILE, furthestEnemy)
                      #  continue
                    
            #allEnemyGroundUnits: Units = self.enemy_units.not_flying
            #if allEnemyGroundUnits:
             #   closestEnemy: Unit = allEnemyGroundUnits.closest_to(ravager)
              #  ravager.move(closestEnemy)
             #   continue  # Continue for loop, don't execute any of the following

            # Move to random enemy start location if no enemy buildings have been seen
            #ravager.move(self.enemy_start_locations[0])    
                   # placement = closestEnemy
                    
                   # ravager(AbilityId.EFFECT_CORROSIVEBILE, placement) 
                  
                   
    #async def warpgate_research(self):
       # if(
         #   self.structures(UnitTypeId.CYBERNETICSCORE).ready
          #  and self.can_afford(AbilityId.RESEARCH_WARPGATE)
          #  and self.already_pending_upgrade(UpgradeId.WARPGATERESEARCH) == 0
       # ):
        #    cybercore = self.structures(UnitTypeId.CYBERNETICSCORE).ready.first
        #    cybercore.research(UpgradeId.WARPGATERESEARCH)
            
    
        #ravagercount = self.units(UnitTypeId.RAVAGER).amount
        #ravagers = self.units(UnitTypeId.RAVAGER).ready
        
       # if self.structures(UnitTypeId.PYLON).ready:
        #    proxy = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0])
         #   proxyposition = proxy.position.random_on_distance(3)
        
        #if ravagercount > 6:
            #for ravager in ravagers:
              #  ravager.attack(self.enemy_start_locations[0])
           # else:
               # ravager.attack(proxyposition)
               
        
               
   # async def warp_stalkers(self):
      #  for warpgate in self.structures(UnitTypeId.WARPGATE).ready:
         #   abilities = await self.get_available_abilities(warpgate) #is warpgate finished?
          #  proxy = self.structures(UnitTypeId.PYLON).closest_to(self.enemy_start_locations[0])
          #  if AbilityId.WARPGATETRAIN_STALKER in abilities and self.can_afford(UnitTypeId.RAVAGER):
           #     placement = proxy.position.random_on_distance(3) 
           #     warpgate.warp_in(UnitTypeId.RAVAGER, placement)
    
                
   
               
    

            def on_end(self, result):
                                    print("Game ended.")
        # Do things here after the game ends
