# Wikipedia Game (Semantic meaning)
The objective is to find the name of the article on Wikipedia. Player can do this by filling up the article with words, collecting hints which may help to guess which article is it. The game is based on the Wikipedia API.

## How to play
1. Run the game by `flask --app . run` in the repository directory.
2. Start guessing words that the article contains. You can use as many words as you want. **The game is going to leave hints if the entered words have similar semantic meaning to the one that acutally appears in the article.**
3. You win, when you guess the article name correctly.

The game is based on the semantic meaning of the words. Frequently, similar word forms will be filled when playing, so that if the player guesses the word *biology* the game will also look for *biological* or *biologist*.


# Screenshots
![](/img/game.png)