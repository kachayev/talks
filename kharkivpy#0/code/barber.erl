-module(barber).
-export([run/2, barber/1, clients/1, simulator/2]).

-define(CUT_DUTAION, 20).

%% XXX: links, monitors etc are not used to focus on messaging!!!
%% XXX: use records instead of long tuples

run(RoomSize, Duration) ->
    % create barber
    BPid = spawn(?MODULE, barber, [?CUT_DUTAION]),
    % run simulartor with barber PID
    SPid = spawn(?MODULE, simulator, [BPid, RoomSize]),
    % spawn clients generator
    CSPid = spawn(?MODULE, clients, [SPid]),
    % create timer to close simulator after duration time
    timer:send_after(Duration, SPid, {close, CSPid}).

barber(Duration) ->
    receive
        {client, Simulator} -> 
            timer:sleep(Duration),
            Simulator ! {barber, done},
            barber(Duration)
    end.

clients(Simulator) ->
    Rnd = 7 + random:uniform(28), % XXX: you can play with constants
    receive
        close -> ok
    after Rnd ->
        Simulator ! {sim, client},
        clients(Simulator)
    end.

simulator({BPid, Status}, {RoomSize, Client, Total}) ->
    case serve_simulation(self(), {BPid, Status}, {RoomSize, Client, Total}) of 
        {S, C, T} -> simulator({BPid, S}, {RoomSize, C, T});
        {close, ClientsGenerator} ->
            ClientsGenerator ! close,
            io:format("Closed! Served clients (~p)~n", [Total]),
            ok
    end;
simulator(Barber, RoomSize) ->
    simulator({Barber, free}, {RoomSize, 0, 0}).

serve_simulation(Me, {BPid, Status}, {RoomSize, Client, Total}) ->
    receive
        {sim, client} when Status == free ->
            io:format("Client goes to barber~n"),
            BPid ! {client, Me},
            {busy, 0, Total};
        {sim, client} when Status == busy, RoomSize > Client ->
            io:format("Client goes to room, new size (~p)~n", [Client+1]),
            {busy, Client+1, Total};
        {sim, client} ->
            io:format("No free space for client, room size (~p)~n", [Client]),
            {busy, Client, Total};
        {barber, done} when Client > 0 -> 
            io:format("Take client from room, new size (~p)~n", [Client-1]),
            BPid ! {client, Me},
            {busy, Client-1, Total+1};
        {barber, done} -> 
            io:format("Barber finished, idle~n", []),
            {free, 0, Total+1};
        {close, ClientsGenerator} -> {close, ClientsGenerator}
    end.