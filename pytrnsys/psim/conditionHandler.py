class conditionHandler:

    COMP_OPS = ['=', '<', '>']

    def conditionDictGenerator(self, plotVariables):
        conditionDict = {}
        for plotVariable in plotVariables:
            if any(char in plotVariable for char in self.COMP_OPS):
                if '<' in plotVariable:
                    ineqCounter = plotVariable.count('<')
                    if ineqCounter == 1:
                        if '<=' in plotVariable:
                            conditionEntry, conditionValue = plotVariable.split('<=')
                            conditionValue = '<=' + conditionValue
                        else:
                            conditionEntry, conditionValue = plotVariable.split('<')
                            conditionValue = '<' + conditionValue
                    elif ineqCounter == 2:
                        conditionEntry = plotVariable.split('<')[1]
                        conditionEntry = conditionEntry.replace('=', '')
                        conditionValue = 'RANGE:' + plotVariable
                    else:
                        raise ValueError('Incorrect range statement: ' + plotVariable)
                    conditionDict[conditionEntry] = conditionValue
                elif '>' in plotVariable:
                    conditionEntry, conditionValue = plotVariable.split('>')
                    conditionValue = '>' + conditionValue
                    conditionDict[conditionEntry] = conditionValue
                elif '=' in plotVariable:
                    conditionEntry, conditionValue = plotVariable.split('=')
                    if '|' in conditionValue:
                        conditionValue = 'LIST:' + conditionValue
                    else:
                        conditionValue = '==' + conditionValue
                    conditionDict[conditionEntry] = conditionValue

        return conditionDict

    def conditionChecker(self, conditionDict, resultsDict):
        for conditionEntry in conditionDict:
            conditionValue = conditionDict[conditionEntry]
            if 'RANGE:' in conditionValue:
                conditionValue = conditionValue.replace('RANGE:', '')
                conditionValue = conditionValue.replace(conditionEntry, str(resultsDict[conditionEntry]))
                conditionEntryFulfilled = eval(conditionValue)
            elif 'LIST:' in conditionValue:
                conditionValue = conditionValue.replace('LIST:', '')
                valueList = conditionValue.split('|')
                agreementList = []
                for valueEntry in valueList:
                    try:
                        valueEntry = float(valueEntry)
                    except:
                        pass
                    agreementList.append(resultsDict[conditionEntry] == valueEntry)
                conditionEntryFulfilled = any(agreementList)
            else:
                isNumber = True
                if '==' in conditionValue:
                    rawConditionValue = conditionValue.split('==')[-1]
                    try:
                        float(rawConditionValue)
                    except:
                        isNumber = False
                        conditionValue = rawConditionValue

                conditionEntryFulfilled = eval('resultsDict[conditionEntry]' + conditionValue) if isNumber \
                    else resultsDict[conditionEntry] == conditionValue

            if not (conditionEntryFulfilled):
                return False

        return True