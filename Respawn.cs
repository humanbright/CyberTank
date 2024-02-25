using UnityEngine;

public class RespawnObject : MonoBehaviour
{
    public float respawnDelay = 2.0F;


    public void DisableAndRespawn()
    {
        // Disable the object
        gameObject.SetActive(false);

        // Call respawn after a delay
        Invoke(nameof(Respawn), respawnDelay);
    }

    // can add parameter to change where you want to respawn the item
    private void Respawn()
    {
        // Enable the object at the desired position
        gameObject.transform.position = new Vector3(-2.04F, 0.68F, 2.48F); // Reset position if needed
        gameObject.SetActive(true);
    }

    private void OnCollisionEnter(Collision collision)
    {
        if (collision.gameObject.name == "target") {
            // add points
            ScoreDisplay.totalScore += 10;
            
            // Disable object and undisable it "kill and respawn"
            DisableAndRespawn();
        }
    }
}