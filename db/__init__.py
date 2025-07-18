"""_summary_
file    : db/__init__.py
version : 1.0.0
author  : basyair7
date    : 2025
copyright:
    Copyright (C) 2025, basyair7
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>
"""

import os
import sqlite3
from pathlib import Path

class DBConnect:
    """
    A class to handle SQLite database connections and operations.
    """
    def __init__(self, name_db: str=""):
        """
        Initialize the database connection.
        
        Parameters:
        name_db (str): Name of the SQLite database file.
        """
        if not name_db:
            print("Information: Please insert database name file")
            return
        
        self.name_db = name_db
    
    def create(self):
        """
        Create or open the database file.
        """
        connect = sqlite3.connect(self.name_db)
        cursor = connect.cursor()
        
        # Commit the connection to ensure database integrity
        connect.commit()
        
        # Close the database connection
        connect.close()
    
    def insert_data(self, table_name: str, date: str, time: str, chat_id: str, sensor_active: int, status: str):
        """
        Insert data into the specified table. If the table does not exist, it will be created.
        
        Parameters
        table_name (str): Name of the table to insert data into.
        date (str): Date value (TEXT format).
        time (str): Time value (TEXT format).
        chat_id (str): Telegram Chat ID that received the message.
        sensor_active (int): Integer value for counter indicating sensor active.
        status (str): Status of the message delivery ("success" or "failed").
        """
        try:
            # Validate the table name
            if not table_name:
                raise ValueError("Please insert table name")
            
            if not table_name.isidentifier():
                raise ValueError("Invalid table name")
            
            # Connect to the SQLite database
            connect = sqlite3.connect(self.name_db)
            cursor = connect.cursor()
            
            # Create table if it does not exist
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS "{table_name}" (
                    date TEXT, 
                    time TEXT,
                    chat_id TEXT,
                    sensor_active INTEGER,
                    status TEXT
                );
            """)
            
            connect.commit()
            
            # Insert data into the table
            cursor.execute(f"""
                INSERT INTO "{table_name}" (date, time, chat_id, sensor_active, status) 
                VALUES (:date, :time, :chat_id, :sensor_active, :status);
            """, {
                'date': date, 
                'time': time, 
                'chat_id': chat_id,
                'sensor_active': sensor_active,
                'status': status
            })
            
            connect.commit()
        
        except Exception as e:
            print("Error: ", e)
            
        finally:
            # Ensure the database connection is closed properly
            connect.close()
            
    def store_chatID(self, table_name: str, chat_id: str):
        """
        Store chat_id data into the specified table. If the table does not exist, it will be created.
        
        Parameters:
        table_name (str): Name of the table to insert data into.
        chat_id(str): chat_id value (TEXT format).
        """
        try:
            # Validate table name
            if not table_name:
                raise ValueError("Please insert table name")
            if not table_name.isidentifier():
                raise ValueError("Invalid table name")
            
            # Connect to the SQLite database
            connect = sqlite3.connect(self.name_db)
            cursor = connect.cursor()
            
            # Create table if it does not exist
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS "{table_name}" (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id TEXT UNIQUE
                );
            """)
            
            # Insert chat_id only if it doesn't already exist
            cursor.execute(f"""
                INSERT OR IGNORE INTO "{table_name}" (chat_id) VALUES (?);
            """, (chat_id,))
            
            connect.commit()
            
        except Exception as e:
            print("Error: ", e)
        
        finally:
            # Ensure the database connection is closed properly
            connect.close()
            
    def load_chat_ids(self, table_name: str):
        """
        Load all chat IDs from the database.
        
        Parameters:
        table_name (str): The name of the table where chat IDs are stored.
        
        Returns:
        A set containing unique chat IDs
        """
        try:
            # Validate table name
            if not table_name or not table_name.isidentifier():
                raise ValueError("Invalid table name")

            # Connect to the database
            connect = sqlite3.connect(self.name_db)
            cursor = connect.cursor()

            # Retrieve all chat IDs from the table
            cursor.execute(f"SELECT chat_id FROM {table_name}")
            rows = cursor.fetchall()  # Fetch all query results
            
            if not rows:
                return None  # Or return 0 if you prefer to indicate no data found
        
            # Store chat IDs in a set to ensure uniqueness
            chat_ids = {row[0] for row in rows}
            
            # print(f"Loaded {len(chat_ids)} chat IDs from the database.")
            return chat_ids

        except Exception as e:
            print(f"Error loading chat IDs: {e}")
            return set()  # Return an empty set if an error occurs
        
        finally:
            # Close the database connection
            connect.close()
            
    def remove_chatID(self, table_name: str, chat_id: str):
        """
        Remove a specific chat_id from the specified table.
        
        Parameters:
        table_name (str): Name of the table to remove data from.
        chat_id (str): The chat_id to remove (TEXT format).
        
        Returns:
        status (boolean)
        """
        
        try:
            # Validate table name
            if not table_name:
                raise ValueError("Please insert table name")
            if not table_name.isidentifier():
                raise ValueError("Invalid table name")
            
            # Connect to the SQLite database
            connect = sqlite3.connect(self.name_db)
            cursor = connect.cursor()
            
            # Remove the chat_id from the table
            cursor.execute(f"""
                DELETE FROM "{table_name}" WHERE chat_id = ?;
            """, (chat_id,))
            
            connect.commit()
            # print(f"Chat ID {chat_id} remove successfully from {table_name}.")
            status = True
            
        except Exception as e:
            print("Error: ", e)
            status = False    
        
        finally:
            connect.close()
            return status