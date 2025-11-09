import { useState, useEffect, useCallback } from 'react';

const useUserLimits = (maxCount = 10) => {
  const [questionCount, setQuestionCount] = useState(0);

  useEffect(() => {
    const savedCount = localStorage.getItem('questionCount');
    if (savedCount) {
      setQuestionCount(Number(savedCount));
    }
  }, []);

  const incrementCount = useCallback(() => {
    const newCount = questionCount + 1;
    setQuestionCount(newCount);
    localStorage.setItem('questionCount', newCount.toString());
  }, [questionCount]);

  const hasReachedLimit = questionCount >= maxCount;
  const remainingQuestions = maxCount - questionCount;

  return { questionCount, incrementCount, hasReachedLimit, remainingQuestions };
};

export default useUserLimits;

