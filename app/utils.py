import requests
import json
import pymongo
import os
import ast
#######
#
# queryParameters list of dictionaries
#
#########
def validParameters(queryParameters):

    for parameter in queryParameters:

        if parameter is None:

            continue

        parameterName = parameter['parameter']

        if 'error' in parameter.keys():

            return False, parameterName + ' not formatted properly'

        if parameterName in ['birthWeight','gestationalAge','outcomePMA']:

            for key in parameter:

                if key not in ['parameter','lt','lte','gt','gte','nin','ne','eq','value']:

                    return False,parameterName + ' contains key outside of lt,lte,gt,gte,nin,ne,eq'

    return True,''
def buildQuery(queryParamaters):

    query = {}

    for parameterDict in queryParamaters:

        if parameterDict is None:

            continue

        parameter = parameterDict['parameter']
        print(parameter)
        if 'value'in parameterDict.keys():

            query[parameter] = parameterDict['value']

        else:
            query[parameter] = {}

            for key in parameterDict:

                if key == 'parameter':

                    continue

                if key in ['lt','lte','gt','gte']:

                    query[parameter]['$' + key] = parameterDict[key]

                else:

                    continue
    return query

def getQueryParameter(parameter,request):

    parameterDict = request.args.get(parameter)

    if parameterDict is not None:

        try:

            result = ast.literal_eval(parameterDict)

            if isinstance(result,dict):

                result['parameter'] = parameter

            else:

                result = {'parameter':parameter,'value':result}

            return result

        except:

            return {'error':"parameter not valid json",'parameter':parameter}

    return None

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
