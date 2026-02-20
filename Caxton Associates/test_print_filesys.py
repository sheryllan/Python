#!/usr/bin/env python3
"""Test script for print_filesys function"""

import os
import tempfile
import shutil
from print_filesys import print_filesys, print_filesys_recursive, print_filesys_memo
from unittest.mock import patch

def create_test_structure():
    """Create a test directory structure similar to the example"""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp(prefix="test_filesys_")
    
    # Create the structure: temp/2023/11/07 and temp/2024/01/12, temp/2024/01/15
    os.makedirs(os.path.join(temp_dir, "2023", "11", "07"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "2024", "01", "12"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "2024", "01", "15"), exist_ok=True)
    
    # Create some test files
    with open(os.path.join(temp_dir, "2023", "11", "07", "file1.txt"), "w") as f:
        f.write("test")
    with open(os.path.join(temp_dir, "2024", "01", "12", "file2.txt"), "w") as f:
        f.write("test")
    with open(os.path.join(temp_dir, "2024", "01", "file3.txt"), "w") as f:
        f.write("test")
    
    return temp_dir

# def test_print_filesys():
#     """Test the print_filesys function"""
#     test_dir = create_test_structure()
    
#     print("Testing print_filesys function:")
#     print("=" * 50)
#     print_filesys(test_dir)
#     print("=" * 50)
    
#     # Cleanup
#     shutil.rmtree(test_dir)
#     print("\nTest completed. Temporary directory cleaned up.")


@patch('print_filesys.isfile')
@patch('print_filesys.isdir')
@patch('print_filesys.os.listdir')
def test_print_filesys_recursive(mock_listdir, mock_isdir, mock_isfile):
    mock_isfile.side_effect = lambda path: path.endswith('.txt')
    mock_isdir.side_effect = lambda path: not path.endswith('.txt')

    directory_map = {
        'temp': ['2023', '2024', 'annual_report.txt'],
        'temp/2023': ['11'],
        'temp/2024': ['01'],
        'temp/2023/11': ['07', 'monthly_report.txt'],
        'temp/2024/01': ['12', '15'],
        'temp/2023/11/07': ['daily_report1.txt'],
        'temp/2024/01/12': ['daily_report2.txt'],
        'temp/2024/01/15': ['daily_report3.txt'],
    }
    mock_listdir.side_effect = lambda path: directory_map[path]
    # print_filesys_recursive('temp')
    print_filesys_memo('temp')



if __name__ == '__main__':
    test_print_filesys_recursive()