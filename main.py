from polygen import random_polygon
import random
    
    
def main():
	random.seed(5)
	j = 0
	f = open('dataset.csv', 'w')
	f.write("WKT,id")

	while j < 100:
		i = 0
		n = random.randint(3, 20)
		polygon = random_polygon(num_points=n)
		f.write('\n"[[[')

		while i < n:
			s = str(tuple([polygon[i][0] * 180, polygon[i][1] * 90]))
			s = s.replace(', ', ',')
			f.write(s)
			if i != n-1:
				f.write(',')
			i += 1
			
		f.write(']]]",')
		f.write('"' + str(j) + '"')
		j += 1

	f.close()
	
	
main()
