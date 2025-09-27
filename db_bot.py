import json
from openai import OpenAI
import os
import sqlite3
from time import time
from setup import setup

print("Running db_bot.py!")
fdir = os.path.dirname(__file__)

# setup()

def getPath(fname):
	return os.path.join(fdir, fname)

sqliteDbPath = getPath("aidb.sqlite")
setupSqlPath = getPath("setup.sql")

sqliteCon = sqlite3.connect(sqliteDbPath)
sqliteCursor = sqliteCon.cursor()

def runSql(query):
	result = sqliteCursor.execute(query).fetchall()
	return result

# OPENAI
configPath = getPath("config.json")
print(configPath)
with open(configPath) as configFile:
	config = json.load(configFile)

openAiClient = OpenAI(api_key = config["openaiKey"])
openAiClient.models.list() # check if the key is valid (update in config.json)

def getChatGptResponse(content):
	stream = openAiClient.chat.completions.create(
		model="gpt-4o",
		messages=[{"role": "user", "content": content}],
		stream=True,
	)

	responseList = []
	for chunk in stream:
		if chunk.choices[0].delta.content is not None:
			responseList.append(chunk.choices[0].delta.content)

	result = "".join(responseList)
	return result

with (open(setupSqlPath) as setupSqlFile):
	setupSqlScript = setupSqlFile.read()

# strategies
commonSqlOnlyRequest = " Give me a sqlite select statement that answers the question. Only respond with sqlite syntax. If there is an error, do not explain it!"
strategies = {
	"zero_shot": setupSqlScript + commonSqlOnlyRequest,
	# "single_domain_double_shot": (setupSqlScript +
	# 			" Name the two airports that have the most distance between them. " +
	# 			"""
	# 				SELECT a1.name AS airport1, a2.name AS airport2
	# 				FROM Airport a1
	# 				JOIN Airport a2 ON a1.airport_id != a2.airport_id
	# 				ORDER BY ((a1.latitude - a2.latitude) * (a1.latitude - a2.latitude) + (a1.longitude - a2.longitude) * (a1.longitude - a2.longitude)) DESC
	# 				LIMIT 1;
	# 			""" +
	# 			commonSqlOnlyRequest)
}

questions = [
	# "What are the top 5 busiest airports, and how many incoming and outgoing routes do they have?",
	# "Which type of aircraft is most used by the airline that has the most routes, and what is the airline?",
	# "Which country has the most airports, and how many airports does it have?",
	# "Which country has the most incoming flights, and how many incoming flights does it have?",
	# "Which country has the most outgoing flights, and how many outgoing flights does it have?",
	# "How many airports are there below sea level? Count how many, and name as many as five of them.",
	"How many layovers do you need if you start at SLC (Salt Lake City) and end at ICN (Incheon)?"
	# "What route (source and destination airport) is most common among all the different airlines? Tell me the names of the airports."
	# "Name the two airports that have the most distance between them."
]

def sanitizeForJustSql(value):
	gptStartSqlMarker = "```sql"
	gptEndSqlMarker = "```"
	if gptStartSqlMarker in value:
		value = value.split(gptStartSqlMarker)[1]
	if gptEndSqlMarker in value:
		value = value.split(gptEndSqlMarker)[0]

	return value

for strategy in strategies:
	responses = {"strategy": strategy, "prompt_prefix": strategies[strategy]}
	questionResults = []
	print("########################################################################")
	print(f"Running strategy: {strategy}")
	for question in questions:

		print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
		print("Question:")
		print(question)
		error = "None"
		try:
			getSqlFromQuestionEngineeredPrompt = strategies[strategy] + " " + question
			sqlSyntaxResponse = getChatGptResponse(getSqlFromQuestionEngineeredPrompt)
			sqlSyntaxResponse = sanitizeForJustSql(sqlSyntaxResponse)
			print("SQL Syntax Response:")
			print(sqlSyntaxResponse)
			queryRawResponse = str(runSql(sqlSyntaxResponse))
			print("Query Raw Response:")
			print(queryRawResponse)
			# friendlyResultsPrompt = "I asked a question \"" + question +"\" and the response was \""+queryRawResponse+"\" Please, just give a concise response in a more friendly way? Please do not give any other suggests or chatter."
			betterFriendlyResultsPrompt = "I asked a question: \"" + question +"\" and I queried this database " + setupSqlScript + " with this query " + sqlSyntaxResponse + ". The query returned the results data: \""+queryRawResponse+"\". Could you concisely answer my question using the results data?"
			friendlyResponse = getChatGptResponse(betterFriendlyResultsPrompt)
			print("Friendly Response:")
			print(friendlyResponse)
		except Exception as err:
			error = str(err)
			print(err)

		questionResults.append({
			"question": question,
			"sql": sqlSyntaxResponse,
			"queryRawResponse": queryRawResponse,
			"friendlyResponse": friendlyResponse,
			"error": error
		})

	responses["questionResults"] = questionResults

	with open(getPath(f"response_{strategy}_{time()}.json"), "w") as outFile:
		json.dump(responses, outFile, indent = 2)


sqliteCursor.close()
sqliteCon.close()
print("Done!")
