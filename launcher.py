import asyncio
import src.imdb
import sys

def main():
    if len(sys.argv) != 2:
        if len(sys.argv) < 2:
            print('Error: Not enough arguments provided. Please provide a search term.')
            return
        else:
            print('Error: Too many arguments provided.')
            return

    queryStr = sys.argv[1]
    asyncio.run(src.imdb.search(queryStr))

if __name__ == "__main__":
    main()
