using UnityEngine;

public class Spawn2DObjectOn3DPanel : MonoBehaviour
{
    public GameObject videoFeed; // Assign the 3D panel GameObject in the inspector
    public GameObject target; // Assign the 2D object prefab in the inspector

    // Use this for initialization
    void Start()
    {
        Spawn2DObject();
    }

    void Spawn2DObject()
    {
        // Get the MeshRenderer component of the 3D panel to access its bounds
        MeshRenderer panelRenderer = videoFeed.GetComponent<MeshRenderer>();

        // Assuming the panel is axis-aligned, calculate the min and max bounds
        Vector3 minBounds = panelRenderer.bounds.min;
        Vector3 maxBounds = panelRenderer.bounds.max;

        // Generate a random position within the bounds
        // Note: This assumes the panel is facing the camera in the XY plane
        float randomX = Random.Range(minBounds.x, maxBounds.x);
        float randomY = Random.Range(minBounds.y, maxBounds.y);

        // Determine the Z position to ensure the 2D object appears in front of the 3D panel
        float zPosition = videoFeed.transform.position.z - 0.1f;

        // Instantiate the 2D object at the calculated position
        Vector3 spawnPosition = new Vector3(randomX, randomY, zPosition);
        GameObject spawnedObject = Instantiate(target, spawnPosition, Quaternion.identity);

        // Destroy the object after 5 seconds
        Destroy(spawnedObject, 5f);

        // Spawn a new object after 5 seconds
        Invoke("Spawn2DObject", 5f);
    }
}
