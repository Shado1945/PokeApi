# This application is for getting pokemon data from the Pokedex API

# Note I used Python v 3.11.5, I also used async for functions that took too long to process
# you can run the program as is in the console by calling the main file, python main.py
# I also added test data loops to check necessary functionality on the program, please 
# see the comments

import requests
import asyncio
import aiohttp
from itertools import chain

# Variables
url = "https://pokeapi.co/api/v2/pokemon"

# Function for getting the raw data of the id's for the pokemon
def getPokemonUrl(url,pageSize,pageStart):
    pokemonUrlData = []
    while True:
        # Get request for the API
        pokemonGetRequest = requests.get(f"{url}?offset={pageStart}&limit={pageSize}")

        # Check if the request was a success
        if pokemonGetRequest.status_code == 200:
            dataRequest = pokemonGetRequest.json()
            pokemonUrlData.extend(dataRequest['results'])

            # This is for checking the page size data
            if len(dataRequest['results']) < pageSize:
                break
            else:
                pageStart += pageSize
        else:
            print(f"Request was unsuccessful to retrieve data: {pokemonGetRequest.status_code}")
            break
    return pokemonUrlData

# Used async below as loops where taking too long

# Async function for retrieving the pokemon on a single http request
async def fetchPokemonData(asyncSession,url):
    async with asyncSession.get(url) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"Request was unsuccessful to retrieve data from {url}")
            return None

# async function for handling multiple pokemon url requests, it uses async.gather that improves
# the speed of getting data from multiple url's  
async def getPokemonData(pokemonUrlList):
    async with aiohttp.ClientSession() as asyncSession:
        requests = [fetchPokemonData(asyncSession, pokemon['url']) for pokemon in pokemonUrlList]
        pokemonAll = await asyncio.gather(*requests)
        # The code bellow is for filtering out none values
        filterPokemonList = list(filter(lambda pokemon: pokemon is not None, pokemonAll))
        return filterPokemonList

# Creating the pokemon list
def pokemonList(pokemonData):
    return [
        {
            'id': pokemonRaw['id'],
            'name': pokemonRaw['name'],
            'types': ', '.join(map(lambda t: t['type']['name'], pokemonRaw['types'])),
            'abilities': ', '.join(map(lambda a: a['ability']['name'], pokemonRaw['abilities']))
        }
        for pokemonRaw in pokemonData
    ]

# Getting all the pokemon types from list
def getPokemonType(pokemonData):
    pokemonTypes = list(chain.from_iterable(map(lambda p: map(lambda t: t['type']['name'], p['types']), pokemonData))) 
    return list(set(pokemonTypes))

# categorize pokemon by type
def groupPokemonByType(typeOfPokemon, pokemon):
    groupedPokemon = {type: list(filter(lambda p: type in p['types'].split(', '), pokemon)) for type in typeOfPokemon}
    return groupedPokemon

# This function is for displaying the data
def showDisplay(groupedPokemon):
    for type, pokemons in groupedPokemon.items():
        print(type)
        print("*****************************************************************************************************")
        for pokemonEach in pokemons:
            print(f"    NAME: {pokemonEach['name']} ABILITIES: {pokemonEach['abilities']}")
        print()

# Getting URLs of all Pokemon
pokemonUrls = getPokemonUrl(url, 1000, 0)

# Test return result for URL of pokemon
'''
for url in pokemonUrls:
    print(url)
'''
# Getting detailed data of each Pokemon
pokemonData = asyncio.run(getPokemonData(pokemonUrls))

# Test detailed data of each pokemon, This list of data is very big
# and also unformated
'''
for pokemonRaw in pokemonData:
    print(pokemonRaw)
'''
# Pokemon types
typeOfPokemon = getPokemonType(pokemonData)

# Test data of pokemon types
'''
for pokemonType in typeOfPokemon:
    print(pokemonType)
'''
# The Pokemon itself
pokemon = pokemonList(pokemonData)

# Test data of pokemons
'''
for iChooseyou in pokemon:
    print(iChooseyou)
'''

# Group Pokemon by type
pokemonGroup = groupPokemonByType(typeOfPokemon, pokemon)

# Displaying the data 
showDisplay(pokemonGroup)

