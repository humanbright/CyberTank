using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class ScoreDisplay : MonoBehaviour
{
    public static int totalScore = 0;
    public int internalScore;
    public GameObject Score;

    // on restart total score is 0
    public void Start() {
        totalScore = 0;
    }
    
    public void Update() {
        internalScore = totalScore;
        Score.GetComponent<Text>().text = "Score" + internalScore;
    }
}