# OpenAI API Bot Starter

Clone this repository, then paste your OpenAI Developer Platform API key inside the `.env` file.

## 1) Clone the project

```bash
git clone <your-repo-url>
cd OpenAI_Developer_Platform_Demo
```

## 2) Add your API key to `.env`

Create or open `.env` and add:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 3) Install dependencies

```bash
pip install openai python-dotenv
```

## 4) Run the original mentor bot

```bash
python main.py
```

## 5) Run the new adapted bot

```bash
python innovation_bot.py
```

---

## What changed in the new file?

`innovation_bot.py` is inspired by the mentor bot structure but changes:

- Model
- Role
- Prompt style
- Output format

It acts as a product innovation advisor instead of a hackathon mentor.



