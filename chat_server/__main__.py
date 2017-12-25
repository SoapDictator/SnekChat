import server.serverSocket

def main():

		ascii_snek = """\
    --..,_                     _,.--.
       `'.'.                .'`__ o  `;__.
          '.'.            .'.'`  '---'`  `
            '.`'--....--'`.'
              `'--....--'`
"""
			
		print(ascii_snek)
		
		server.serverSocket.__init__()

		# Do argument parsing here (eg. with argparse) and anything else
		# you want your project to do.

if __name__ == "__main__":
		main()