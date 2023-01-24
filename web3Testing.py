# imports
from web3 import Web3, HTTPProvider
from polygonscan import PolygonScan
from ratelimiter import RateLimiter
from pycoingecko import CoinGeckoAPI

# API rate limiter to ensure I don't go over my calls per second
rate_limiter = RateLimiter(max_calls=3, period=2)
def getTokens():
    # instantiate a web3 remote provider
    endPoint = 'https://matic.getblock.io/6740c819-7a27-4382-93c2-d029ac4b0a97/mainnet/'
    try:
        w3 = Web3(HTTPProvider(endPoint))
    except Exception as err:
        print(err)

    # the unique tx hash of the tx being queries
    txHash = '0x0053490215baf541362fc78be0de98e3147f40223238d5b12512b3e26c0a2c2f'
    # the tx receipt for to gather all tokens which were traded
    txDict = w3.eth.get_transaction_receipt(txHash)
    tokenAdressList = [str(eachElement.address) for eachElement in txDict.logs]
    # this takes each element inside of the list and map it a dictionary deleting any   duplicates and assign NO values inside of the dictionary - from stackoverflow
    uniqueTokenAddressList = list(dict.fromkeys(tokenAdressList))
    # dict for storing token details
    tokenDict = {}
    for eachAddress in uniqueTokenAddressList:
        # we need the unique abi of each specific address
        with PolygonScan("PVS8MXC36JY2HT1IX1JSKT3WYJPK4JYJTM",False) as matic:
            abi = matic.get_contract_abi(eachAddress)
        # the contract of the given address
        tokenContract = w3.eth.contract(address=eachAddress, abi=abi)
        with rate_limiter:
            # contrainsts to look for ONLYERC20 Tokens based on what is usually found in them 
            erc20TokenFunctionList = ['<Function balanceOf(address)>', '<Functionname()>', '<Function totalSupply()>', '<Function symbol()>', '<Functiondecimals()>', '<Function transfer(address,uint256)>']

            # gets ALL functions belonging to a smart contract address, turns them into strings for better parsing
            allTokenFunctionsList = [str(eachElement) for eachElement in tokenContract.all_functions()]

            if set(erc20TokenFunctionList).intersection(allTokenFunctionsList):
                tokenSymbol = tokenContract.functions.symbol().call()
                tokenName = tokenContract.functions.name().call()
                tokenDecimals = tokenContract.functions.decimals().call()
                cg = CoinGeckoAPI()
                if cg.search(tokenSymbol)['coins'] != []:
                    tokenDict.update({f"{tokenSymbol}":[tokenName,tokenDecimals,eachAddress]})
    #print(tokenDict)
    return tokenDict