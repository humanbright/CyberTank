using UnityEngine;
using UnityEngine.XR;

public class SimpleShoot : MonoBehaviour
{
    public GameObject circlePrefab; // Assign your circle prefab in the inspector
    public Transform shootPoint; // Assign the point from where the circle will be shot
    public float shootForce = 500f; // Adjust the shooting force

    // Update is called once per frame
    void Update()
    {
        // Check for input from the right-hand controller trigger
        if (Input.GetButtonDown("Fire1") || CheckTriggerPressed(XRNode.RightHand))
        {
            Shoot();
        }
    }

    bool CheckTriggerPressed(XRNode hand)
    {
        InputDevice device = InputDevices.GetDeviceAtXRNode(hand);
        device.TryGetFeatureValue(CommonUsages.trigger, out float triggerValue);
        return triggerValue > 0.1f; // Adjust trigger threshold as needed
    }

    void Shoot()
    {
        GameObject circle = Instantiate(circlePrefab, shootPoint.position, shootPoint.rotation);
        
        // Add a Rigidbody component to your circle prefab beforehand for physics
        Rigidbody2D rb = circle.GetComponent<Rigidbody2D>(); // Use Rigidbody for 3D objects

        // Apply a force to shoot the circle
        rb.AddForce(shootPoint.up * shootForce);
    }
}
