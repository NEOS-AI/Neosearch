from sentence_transformers import CrossEncoder

model = CrossEncoder('model_name', max_length=512)
scores = model.predict(
    [
        ('Query', 'Paragraph1'),
        ('Query', 'Paragraph2'),
        ('Query', 'Paragraph3'),
    ]
)
