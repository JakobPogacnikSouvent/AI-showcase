% import model

<!DOCTYPE html>
<html>
    <body>
        <h1>Rock Paper Scissors</h1>
        <h2>P1: {{game.get_player_choice()}}</h2>
        <h2>CPU: {{game.get_computer_choice()}}</h2>
        <h2>WINNER: {{game.winner}}</h2>
        

        <form action="/rps/{{game_id}}/" method="post">
            <input type="hidden" name='player_choice' value='rock'>
            <button type="submit">Rock</button>
        </form>

        <form action="/rps/{{game_id}}/" method="post">
            <input type="hidden" name='player_choice' value='paper'>
            <button type="submit">Paper</button>
        </form>

        <form action="/rps/{{game_id}}/" method="post">
            <input type="hidden" name='player_choice' value='scissors'>
            <button type="submit">Scissors</button>
        </form>

    </body>
</html>
