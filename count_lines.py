import os
import re
from dotenv import load_dotenv

load_dotenv()

import inspect
from openai import OpenAI

from openai import OpenAI
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel
   

client = OpenAI()

# func = client.responses.create
# print("openai version:", openai.__version__)
# print("responses.create signature:", inspect.signature(openai.OpenAI().responses.create))


class TargetMusclePart(BaseModel):
    muscle_group: str
    muscle_part: List[str]
class PlannedExercise(BaseModel):
    exercise_name: str
    target_muscle_part: List[TargetMusclePart]
    reps: str
    weight: str
    rest_time: float
    alternative_exercise: str
    alternative_exercise_reps: str
    alternative_exercise_weight: str
class PlannedSet(BaseModel):
    set_number: int
    set_duration: float
    set_strategy: str
    num_rounds: int
    target_muscle_group: List[str]
    set_reasoning: str
    exercises: List[PlannedExercise]


client = OpenAI()

class WorkoutPlannerOutput(BaseModel):
    sets: List[PlannedSet]
    workout_explanation: str


json_schema = WorkoutPlannerOutput
response = client.responses.parse(
    model="gpt-5-mini",
    input=[
        {"role": "system", "content": "You return workout plans as JSON for a glutes woman"},
        {"role": "user", "content": "Build a beginner plan."},
    ],
    text_format= WorkoutPlannerOutput
)
print(response.output_text)


def count_code_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    total = len(lines)
    imports = 0
    blank = 0
    comments = 0
    code = 0
    
    in_multiline_comment = False
    multiline_comment_lines = 0
    
    for line in lines:
        stripped = line.strip()
        
        # Check for multiline comments (/* ... */)
        if '/*' in line:
            in_multiline_comment = True
            multiline_comment_lines += 1
            if '*/' in line:
                in_multiline_comment = False
            continue
            
        if in_multiline_comment:
            multiline_comment_lines += 1
            if '*/' in line:
                in_multiline_comment = False
            continue
        
        # Empty line
        if not stripped:
            blank += 1
        # Single-line comment
        elif stripped.startswith('//'):
            comments += 1
        # Import/export statement
        elif stripped.startswith('import ') or stripped.startswith('from ') or stripped.startswith('export '):
            imports += 1
        # Actual code
        else:
            code += 1
    
    return {
        'total': total,
        'imports': imports,
        'blank': blank,
        'comments': comments,
        'multiline_comments': multiline_comment_lines,
        'code': code
    }

# paths = ['components', 'hooks','screens', 'services','types', '']
# # Target directory - recursively find all .ts and .tsx files
# for path in paths:
#     target_dir = 'react-native-frontend/src/' + path
#     ts_files = []

#     for root, dirs, files in os.walk(target_dir):
#         for file in files:
#             if file.endswith('.ts') or file.endswith('.tsx'):
#                 file_path = os.path.join(root, file)
#                 ts_files.append(file_path)

#     print('=' * 80)
#     print('TYPESCRIPT CODE LINE COUNT ANALYSIS (excluding imports)')
#     print('=' * 80)
#     print()

#     total_code = 0
#     results = []

#     for file_path in sorted(ts_files):
#         counts = count_code_lines(file_path)
#         results.append((file_path, counts))
#         total_code += counts['code']
        
#     for file_path, counts in results:
#         # Display relative path from target_dir
#         display_path = file_path.replace(target_dir + os.sep, '')
#         print(f'{display_path}')
#         print(f'  Total lines:          {counts["total"]:>4}')
#         print(f'  Import/export:        {counts["imports"]:>4}')
#         print(f'  Blank lines:          {counts["blank"]:>4}')
#         print(f'  Comment lines:        {counts["comments"]:>4}')
#         print(f'  Multiline comments:   {counts["multiline_comments"]:>4}')
#         print(f'  ACTUAL CODE LINES:    {counts["code"]:>4}')
#         print()

#     print('=' * 80)
#     print(f'TOTAL ACTUAL CODE LINES (all files): {total_code}')
#     print('=' * 80)
