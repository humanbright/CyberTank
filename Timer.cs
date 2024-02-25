using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class Timer : MonoBehaviour
{
    // 60 seconds
    public static float remainingTime;
    public float internalTimer;
    public GameObject TimerTxt;

    public void Update() {
        if (remainingTime > 0) {
            remainingTime = remainingTime - Time.deltaTime;
        }
        if (remainingTime < 0) {
            remainingTime = 0;
        }

        // internalTimer = remainingTime;
        // TimerTxt.GetComponent<Text>().text = "Time Left: " + internalTimer;
    }

}