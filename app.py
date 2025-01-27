from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def cadastro():
	if request.method == "POST"
		nome = request.form.get("concurso_name")
		data = request.form.get("concurso_date")
		banca = request.form.get("concurso_banca")


		#processar e salvar dados
		print(f"Concurso: {name}, Data: {data}, Banca: {banca}")

		return f"Concurso '{name} cadastrado com sucesso!"

	return render_template("index.html")

if __name__ == "__main__":
	app.run(debug=True)
