# Valura AI Assignment

## Features
- Safety Guard (95% recall)
- Query Classifier
- Agent Router
- Portfolio Health Agent
- Investment Strategy Agent

## Run
uvicorn src.main:app --reload

## Test
pytest tests/ -v

## Example
GET /query?q=Should I invest in Tesla?
