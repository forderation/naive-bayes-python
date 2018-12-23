# author kharisma muzaki ghufron 
# 09 December 2018
# Universitas Muhammadiyah Malang
# cara memakai:
# buka cmd arahkan ke lokasi hagoML.py, ketikan perintah python hagoML.py atau python3 hagoML.py
# buka browser ketikkan localhost:5000?message='apa yang mau di test?
# perhitungan lihat di: https://monkeylearn.com/blog/practical-explanation-naive-bayes-classifier/
import re
import csv
#jadi re ini library/module (ekspresi reguler) buat menghilangkan tanda yang diinginkan misalkan kata
#dengan karakter tanda titik atau koma dsb, akan dihilangkan
from collections import defaultdict
#ini merupakan tipe data mirip hash map namanya dictionary
from flask import Flask, request, jsonify
import os, json
#kalau yang flask, os, dan json lebih ke arah buat web server local buat menampilkan hasilnya
app = Flask(__name__)
file = open("training_hago.csv", "r", encoding='utf-8')
#membuka file dataset dengan path  yang sudah include jadi satu folder dengan hagoML.py 
dataset = file.read().lower().splitlines()
#semua baris akan kalimatnya dijadikan lowercase dan setiap baris dipisah menjadi struktur data list
words_ya = defaultdict(int)
#ini membuat varibel tipe data dictionary yang akan menampung kata dari hasil target kelasnya 'ya'
words_tidak = defaultdict(int)
#ini membuat varibel tipe data dictionary yang akan menampung kata dari hasil target kelasnya 'tidak'
collection_words = set()
#ini membuat variabel tipe data dictionary tanpa duplikasi kata dari semua hasil target kelas
no_duplicate_total_ya = 0
#menghitung total kata tanpa duplikat dari hasil target kelas 'ya'
no_duplicate_total_tidak = 0
#menghitung total kata tanpa duplikat dari hasil target kelas 'tidak'
del dataset[0]
del dataset[1]
#menghilangkan header dari dataset agar tidak masuk perhitungan
for record in dataset:
#setiap elemen yang ada dalam 'dataset' diassign ke dalam variabel record
    document = re.split(r'[,?". ]+', record)
    #pisahkan setiap kalimat berdasar karakter ,?".(spasi) menjadi sebuah array list
    document = list(filter(None, document))
    # hilangkan hasil semua elemen dalam list yang tidak ada isinya
    # jika ingin hapus kata apakah: words.remove('apakah')
    for word in document[1:]:
    #setiap kata pada document akan dipilah    
        collection_words.add(word)
        #sehingga setiap kata akan dimasukkan dalam struktur tipe data set di collection words
        if (document[0] == 'ya'):
            #jika kata terletak pada target kelas ya
            no_duplicate_total_ya += 1
            #maka increment jumlah kata tanpa duplikasi dengan target ya
            words_ya[word] += 1
            #tambahkan kata pada dictionary sehingga jika sudah ada frekuensinya akan diicrement
        else:
            #jika kata terletak pada target kelas tidak
            no_duplicate_total_tidak += 1
            words_tidak[word] += 1
# penampilan hasil tf dan filtering
with open('hasil_tf.csv','w') as f:
    w = csv.DictWriter(f,dict(words_ya).keys())
    w.writeheader()
    w.writerow(dict(words_ya))
    q = csv.DictWriter(f, dict(words_tidak).keys())
    q.writeheader()
    q.writerow(dict(words_tidak))

print("feature extraction: ")
print("koleksi kata: ")
print(collection_words)
print("total kota jika termasuk duplikat: ", len(collection_words))
print("\ntf | ya:")
print(words_ya)
print("(total semua kata | ya) tanpa duplikasi: ", no_duplicate_total_ya)
print("\ntf | tidak:")
print(words_tidak)
print("(total semua kata | tidak) tanpa duplikasi: ", no_duplicate_total_tidak)
# testing data
@app.route('/', methods=['GET'])
def index():
    tes_question = request.args.get('message', '')
    tes_document = re.split(r'[,?".”/ ]+', tes_question)
    tes_document = list(filter(None, tes_document))
    tes_count_word = defaultdict(int)
    tes_word_ya = defaultdict(float)
    tes_word_tidak = defaultdict(float)
    tes_not_know = defaultdict(int)
    prob_ya = 1
    prob_tidak = 1
    jawaban = ''
    if len(tes_question) > 0:
        for word in tes_document:
            if word in collection_words:
                tes_count_word[word] += 1
                tes_word_ya[word] = (float)((words_ya[word] + 1) /
                                            (no_duplicate_total_ya + len(collection_words)))
                tes_word_tidak[word] = (float)((words_tidak[word] + 1) /
                                               (no_duplicate_total_tidak + len(collection_words)))
            else:
                tes_not_know[word] += 1
        #print("\n", tes_count_word.items())
        #print(tes_word_ya.items())
        #print(tes_word_tidak.items())
        for key, value in tes_word_ya.items():
            tes_word_ya[key] = value ** tes_count_word[key]
            prob_ya *= tes_word_ya[key]
        for key, value in tes_word_tidak.items():
            tes_word_tidak[key] = value ** tes_count_word[key]
            prob_tidak *= tes_word_tidak[key]
        if (prob_ya > prob_tidak):
            jawaban = 'ya'
        else:
            jawaban = 'tidak'
    know = json.dumps([tes_count_word])
    not_know = json.dumps([tes_not_know])
    return jsonify(
        diketahui = json.loads(know), tidak_diketahui = json.loads(not_know),
        pertanyaan = tes_question, probabilitas_ya=prob_ya,
        probabilitas_tidak = prob_tidak,jawaban = jawaban
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True)
