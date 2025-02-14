#include <sourcemod>

public Plugin myinfo = 
{
	name = "test plugin",
	author = "Amandin",
	description = "trying to export kz times so i can overlay later with obs",
	version = "1.0",
	url = ""
};

public OnPluginStart()
{
    HookEvent("round_start", Event_RoundStart);
}

new g_RoundCount;
public void OnMapStart()
{
	// keep track of rounds
	g_RoundCount = 0;
}

public void GOKZ_OnTimerEnd_Post(int client, int course, float time, int teleportsUsed)
{
	// get the player name
	char data[60];
	GetClientName(client, data, sizeof(data));
	
	// format the data to put in the text file
	Format(data, sizeof(data), "%s%s%.2f", data, " ", time);
	
	// for debugging
	PrintToServer("saved data to amandin.txt");
	
	// write the new time to the amandin.txt file
	new Handle:textFile = OpenFile("amandin.txt", "a");
	WriteFileLine(textFile, data);
	CloseHandle(textFile);
}

public Event_RoundStart(Handle:event, const String:name[], bool:dontBroadcast)
{
	// get the round number (0 is for warmup))
	char round[10];
	IntToString(g_RoundCount, round, sizeof(round));
	
	// get the map name
	decl String: map[32];
    GetCurrentMap(map, sizeof(map));
    
    // create a fresh amandin.txt file
	new Handle:textFile = OpenFile("amandin.txt", "w");
	WriteFileLine(textFile, round);
	WriteFileLine(textFile, map);
	CloseHandle(textFile);
	g_RoundCount++;
}