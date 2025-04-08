class Try:
    def __init__(self, nombre):
        self.nombre  = nombre
    
    def show_name(self):
        nombre = self.nombre
        if nombre=="angel":
            a = 5
            return a
        else:
            return("error")
    
    def age(self):
        resultado = self.show_name()
        print(resultado)

persona = Try('angel')
persona.age()