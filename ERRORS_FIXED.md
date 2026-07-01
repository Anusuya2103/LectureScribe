# Errors Found and Fixed in Classroom Minutes Project

## Backend Errors

### 1. Missing Critical Dependencies in requirements.txt
**Issue:** Missing packages required for AI/ML functionality
- `torch` - PyTorch for model inference
- `transformers` - HuggingFace transformers library
- `pyannote.audio` - Speaker diarization model

**Fix:** Added all missing dependencies to `backend/requirements.txt`

### 2. Config Import Conflict
**Issue:** Both `backend/app/config.py` and `backend/app/config/` directory existed, causing import conflicts

**Fix:** Deleted `backend/app/config.py` to use the modular `config/` package structure

### 3. Port Mismatch
**Issue:** Backend was configured to run on port 8001, but frontend expected port 8000

**Fix:** Changed default port in `backend/app/config/settings.py` from 8001 to 8000

### 4. Diarizer Return Type Mismatch
**Issue:** The `diarize()` method returns a `List[Dict]`, but the code in `main.py` was treating it as a dictionary with `.get()` method

**Fix:** Updated `backend/app/main.py` diarization endpoint to:
- Properly handle list return type
- Extract speakers from list of segments
- Create labeled transcript correctly

### 5. Missing Method in Question Generator
**Issue:** `main.py` called `generate_questions_from_lecture()` but this method didn't exist in `question_generator.py`

**Fix:** Added `generate_questions_from_lecture()` method to `backend/app/services/question_generator.py`

## Frontend Errors

### 6. Frontend Model Type Mismatch
**Issue:** `ProcessResponse` model expected `questions` as `List<String>`, but backend returns `List<Dict>` (list of question objects with question, answer, type fields)

**Fix:** Updated `frontend/lib/models/process_response.dart` to expect `List<Map<String, dynamic>>` for questions field

## Additional Fixes (After Testing)

### 7. Missing Method Call in Pipeline
**Issue:** `pipeline.py` was calling `self.diarizer.assign_speakers_to_transcript()` which doesn't exist in the Diarizer class, causing 500 errors during processing

**Fix:** Replaced the non-existent method call with inline logic that properly handles the diarization result (List[Dict]) and creates labeled transcript segments

### 8. Invalid Whisper Model Name
**Issue:** `.env` file had `WHISPER_MODEL=base` instead of the full model identifier `openai/whisper-base`

**Fix:** Updated `backend/.env` to use `WHISPER_MODEL=openai/whisper-base`

### 9. Path Type Mismatch
**Issue:** Config directory paths were strings but code used Path operator `/`, causing "unsupported operand type(s) for /: 'str' and 'str'" error

**Fix:** Convert config paths to Path objects in `backend/app/main.py` after loading

### 10. Question Generation Parameter Error
**Issue:** `num_return_sequences` (5) was greater than `num_beams` (4), causing generation to fail

**Fix:** Changed both parameters to `min(num_questions, 4)` in `question_generator.py`

## Summary

All critical errors have been fixed:
- ✅ Dependencies added
- ✅ Config conflict resolved
- ✅ Port mismatch fixed
- ✅ Diarizer type mismatch fixed
- ✅ Missing method added
- ✅ Frontend model updated
- ✅ Pipeline diarization logic fixed

The application should now be able to:
1. Install all required dependencies
2. Start without import errors
3. Communicate properly between frontend and backend
4. Handle speaker diarization correctly
5. Generate questions from transcripts
6. Parse API responses correctly
7. Process audio files without 500 errors
