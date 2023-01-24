# IMPORT ALL REQUIRED MODULES

from flask import Flask,request,render_template,flash,redirect
import pandas as pd
import random
import pdfkit as pdfm


# INIALIZATIONS
SET_ALPHA=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
Answers={}
SET_NO=0
# set your local host path
LOCAL_HOST='127.0.0.1:5000'
File_Path="static/questions.csv"

app =Flask(__name__)

# CREATING QUESTION AND ANSWER PDFs
# -----------------------------------------------------------------------------------------------------------
@app.route('/genPdf',methods=['POST','GET'])
def genPdf():
    global SET_NO
    n=int(request.args.get("nos"))
    m=int(request.args.get("noq"))

    # path of the wkhtmltopdf.exe
    path_wkthmltopdf = b'C:\Program Files\wkhtmltopdf\\bin\wkhtmltopdf.exe'
    config = pdfm.configuration(wkhtmltopdf=path_wkthmltopdf)
    # convert all question paper to pdf
    for i in range(0,n):

        SET_NO=SET_NO+1
        try:
            url = (f'http://{LOCAL_HOST}/pdf?nos={n}&noq={m}&sa={i}')
            pdfm.from_url(url, f'set_{SET_ALPHA[i]}_questions_.pdf', configuration=config)
            print("done 1")
        except OSError:
            pass
        print(f"saved {i+1} pdf")
    strg = ""
    for k, v in Answers.items():
        strg = strg + "SET " + k + "-> \n"
        for i in range(0,len(v)):
            strg += "         " + str(i+1) + " -> " + SET_ALPHA[v[i]] + "\n"
        strg += "\n\n"

    # convert answers to pdf
    text_file = open("QuestionAndAnswer.txt", "wt")
    n = text_file.write(strg)
    text_file.close()
    pdfm.from_file("QuestionAndAnswer.txt", 'Answers.pdf', configuration=config)

    return "done"


# SHUFFLING AND CREATING WEBPAGE
# -----------------------------------------------------------------------------------------------------------
@app.route('/pdf',methods=['POST','GET'])
def pdf():
    if request.method=='POST':
        set_a=0
        NoQ=int(request.form["NoQ"])
        Nos=int(request.form["NoS"])
    if request.method=='GET':
        set_a=int(request.args.get("sa"))
        Nos = int(request.args.get("nos"))
        NoQ = int(request.args.get("noq"))
    data = pd.read_csv(File_Path)
    questAndAnswer = {}
    answers=[]
    for i in range(0, len(data)):
        Option = []
        finalOption = []
        # read options
        Option.append(data["A"][i])
        Option.append(data["B"][i])
        Option.append(data["C"][i])
        Option.append(data["D"][i])
        answer=data[data["key"][i]][i]
        # shuffle options
        random.shuffle(Option)
        finalOption.append(f"A: {Option[0]}")
        finalOption.append(f"B: {Option[1]}")
        finalOption.append(f"C: {Option[2]}")
        finalOption.append(f"D: {Option[3]}")
        finalOption.append(Option.index(answer))
        questAndAnswer[data["Q"][i]] = finalOption
        # randomise the question
        l = list(questAndAnswer.items())
        random.shuffle(l)
        questAndAnswer = dict(l)
    nq=0
    qVal=[]

    for k in questAndAnswer:
        if nq == NoQ:
            break
        else:
            nq += 1
            qVal.append(k)

    NewquestAndAnswer={}
    for quest in qVal:
        NewquestAndAnswer[quest]=questAndAnswer[quest][:4]
        answers.append(questAndAnswer[quest][4])

    # store all the answers
    Answers[SET_ALPHA[set_a]]=answers
    # print(Answers)
    alpha=SET_ALPHA[set_a]
    return render_template('pdfquestAns.html', quest=NewquestAndAnswer,nos=Nos,noq=NoQ,alpha=alpha)



# HOME PAGE
# SHOW ALL THE QUESTIONS
# -----------------------------------------------------------------------------------------------------------
@app.route('/setQuestion',methods=['POST','GET'])
def setQuestion():
    if request.method == 'POST':
        qcsv = request.files["file"]
        # print(image.filename)
        if qcsv.filename == "":
            return "File Not Found"
        csvPath = File_Path
        qcsv.save(csvPath)
    data = pd.read_csv(File_Path)
    questAndAnswer = {}
    for i in range(0, len(data)):
        Option = []
        finalOption = []

        Option.append(data["A"][i])
        Option.append(data["B"][i])
        Option.append(data["C"][i])
        Option.append(data["D"][i])
        # randomize the options
        random.shuffle(Option)
        finalOption.append(f"A: {Option[0]}")
        finalOption.append(f"B: {Option[1]}")
        finalOption.append(f"C: {Option[2]}")
        finalOption.append(f"D: {Option[3]}")
        questAndAnswer[data["Q"][i]] = finalOption
        # randomise the question
        l = list(questAndAnswer.items())
        random.shuffle(l)
        questAndAnswer = dict(l)
    numberOfQuest=i
    return render_template('questAns.html', quest=questAndAnswer,noq=numberOfQuest)


# INDEX PAGE
# -----------------------------------------------------------------------------------------------------------
@app.route('/',methods=['POST','GET'])
def index():
    return render_template('index.html')


if __name__ =='__main__':
    app.run(debug=True, host='0.0.0.0')
