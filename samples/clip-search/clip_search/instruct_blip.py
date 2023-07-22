import os
import torch
from datasets import load_dataset
from transformers import InstructBlipForConditionalGeneration, InstructBlipProcessor


def create_instruct_blip_model(
    use_cuda_if_available: bool = True,
):
    model = InstructBlipForConditionalGeneration.from_pretrained(
        "Salesforce/instructblip-vicuna-7b",
        load_in_4bit=True,
        torch_dtype=torch.bfloat16,
    )
    processor = InstructBlipProcessor.from_pretrained(
        "Salesforce/instructblip-vicuna-7b"
    )
    return model, processor


def get_datasets_list():
    datasets = [
        ('detection-datasets/fashionpedia', None, 'val'),
        ('keremberke/nfl-object-detection', 'mini', 'test'),
        ('keremberke/plane-detection', 'mini', 'train'),
        ('matthijs/snacks', None, 'validation'),
        ('rokmr/mini_pets', None, 'test'),
        ('keremberke/pokemon-classification', 'mini', 'train'),
    ]
    return datasets


def create_descriptions(
    img_dir: str,
    description_file: str = 'descriptions.csv',
):
    prompt1 = 'Describe this image in full detail. describe each and every aspect of the image so that an artist could re create the image'
    prompt2 = 'Create an extensive description of this image. Be as descriptive as possible.'
    prompts = [prompt1, prompt2]

    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    datasets_list = get_datasets_list()
    model, processor = create_instruct_blip_model()

    counter = 0
    for name, config, split in datasets_list:
        dataset = load_dataset(name, config, split=split)
        for idx in range(len(dataset)):
            img = dataset[idx]['image']
            desc = ''
            for prompt in prompts:
                inputs = processor(
                    images=img,
                    text=prompt,
                    return_tensors="pt"
                ).to(model.device, torch.bfloat16)

                outputs = model.generate(
                    **inputs,
                    do_sample=False,
                    num_beams=10,
                    max_length=512,
                    min_length=16,
                    top_p=0.9, 
                    repetition_penalty=1.5,
                    temperature=1.0,
                )
                generated_text = processor.batch_decode(
                    outputs, skip_special_tokens=True
                )[0].strip()

                desc += generated_text + ' '

            desc = desc.strip()
            img.save(f'{img_dir}/{counter}.jpg')

            with open(description_file, 'a') as f:
                f.write(f'{counter},{desc}\n')
            counter += 1

            if torch.cuda.is_available():
                torch.cuda.empty_cache()
