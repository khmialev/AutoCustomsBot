# Auto Customs Calculator Bot

This Telegram bot helps you calculate customs duty and additional expenses for imported cars. It pulls car data from sources like Copart and Av.by, and stores price information in a PostgreSQL database. The bot offers both basic and special calculation modes and includes functionality to update the database with fresh data.

## Features

- **Customs Duty Calculation:**  
  Calculate customs duty and extra costs (delivery, auction fees, etc.) based on car data.
- **Calculation Modes:**  
  - *Basic Calculation:* Uses engine volume and production year.  
  - *Special Calculation:* Allows you to choose a brand, model, production year, and engine volume.
- **Database Update:**  
  Update the local database with the latest car prices.
- **Asynchronous Processing:**  
  Built with Python's async features and [aiogram](https://docs.aiogram.dev/) for fast performance.
- **Docker Deployment:**  
  Easily run the bot and PostgreSQL in containers using Docker Compose.
