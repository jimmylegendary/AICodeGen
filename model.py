# from transformers import RobertaTokenizer, T5ForConditionalGeneration

# tokenizer = RobertaTokenizer.from_pretrained('Salesforce/codet5-small')
# model = T5ForConditionalGeneration.from_pretrained('Salesforce/codet5-small')

# for i in range(2):
#     file = f'func_data/{i}/input'
#     with open(file, 'rb') as f:
#         text = f.read().decode('utf-8')
#     input_ids = tokenizer(text, return_tensors="pt").input_ids

#     # simply generate a single sequence
#     generated_ids = model.generate(input_ids, max_length=512)
#     print(tokenizer.decode(generated_ids[0], skip_special_tokens=True))

from transformers import RobertaTokenizer, T5ForConditionalGeneration, T5Tokenizer

tokenizer = RobertaTokenizer.from_pretrained('Salesforce/codet5-base')
# tokenizer = T5Tokenizer.from_pretrained('Salesforce/codet5-base')
model = T5ForConditionalGeneration.from_pretrained('Salesforce/codet5-base')

text = "Translate Python to C: if x==0: x += 1"
input_ids = tokenizer(text, return_tensors="pt").input_ids

# simply generate a single sequence
generated_ids = model.generate(input_ids, max_length=20)
print(tokenizer.decode(generated_ids[0], skip_special_tokens=True))
# this prints "user: {user.name}"