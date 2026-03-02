from manim import *
import numpy as np

class ShockleyRamoTheorem(Scene):
    """
    Parametric animation demonstrating the Shockley-Ramo theorem:
    A moving charge induces a current in a nearby electrode proportional to
    the charge times velocity dotted with the weighting field.
    
    I = q * v · E_w
    
    where E_w is the weighting field (field when electrode is at unit potential
    and all other conductors are grounded).
    """
    
    def construct(self):
        # Parameters
        electrode_width = 4
        electrode_height = 0.3
        gap = 3  # Distance between electrodes
        charge_radius = 0.2
        
        # Create electrodes (parallel plate geometry)
        top_electrode = Rectangle(
            width=electrode_width, 
            height=electrode_height,
            fill_color=BLUE,
            fill_opacity=0.8,
            stroke_color=WHITE
        ).shift(UP * gap / 2)
        
        bottom_electrode = Rectangle(
            width=electrode_width,
            height=electrode_height,
            fill_color=BLUE,
            fill_opacity=0.8,
            stroke_color=WHITE
        ).shift(DOWN * gap / 2)
        
        # Labels for electrodes
        top_label = Text("Sensing Electrode", font_size=24).next_to(top_electrode, UP)
        bottom_label = Text("Ground", font_size=24).next_to(bottom_electrode, DOWN)
        
        # Create the moving charge
        charge = Circle(
            radius=charge_radius,
            fill_color=YELLOW,
            fill_opacity=1,
            stroke_color=WHITE
        )
        charge_label = MathTex("+q", font_size=28).move_to(charge)
        charge_group = VGroup(charge, charge_label)
        
        # Starting position (near bottom electrode)
        start_y = -gap / 2 + 0.5
        end_y = gap / 2 - 0.5
        charge_group.move_to([0, start_y, 0])
        
        # Weighting field lines (uniform for parallel plates)
        field_lines = VGroup()
        for x in np.linspace(-electrode_width/2 + 0.3, electrode_width/2 - 0.3, 7):
            arrow = Arrow(
                start=[x, -gap/2 + electrode_height/2, 0],
                end=[x, gap/2 - electrode_height/2, 0],
                buff=0.1,
                color=YELLOW,
                stroke_width=2,
                max_tip_length_to_length_ratio=0.1
            )
            field_lines.add(arrow)
        
        field_label = MathTex(r"\vec{E}_w", font_size=32, color=YELLOW).shift(RIGHT * 3 + UP * 0.5)
        
        # Current indicator (ammeter representation)
        ammeter_pos = RIGHT * 4.5 + UP * gap / 2
        ammeter = Circle(radius=0.4, color=WHITE).move_to(ammeter_pos)
        ammeter_label = Text("A", font_size=24).move_to(ammeter)
        
        # Wire from top electrode to ammeter
        wire1 = Line(
            top_electrode.get_right(),
            ammeter.get_left(),
            color=WHITE
        )
        wire2 = Line(
            ammeter.get_bottom(),
            [ammeter_pos[0], -gap/2, 0],
            color=WHITE
        )
        wire3 = Line(
            [ammeter_pos[0], -gap/2, 0],
            bottom_electrode.get_right(),
            color=WHITE
        )
        circuit = VGroup(wire1, wire2, wire3)
        
        # Current value tracker
        current_tracker = ValueTracker(0)
        
        # Current display
        current_text = always_redraw(
            lambda: MathTex(
                f"I = {current_tracker.get_value():.2f}",
                font_size=32
            ).next_to(ammeter, RIGHT)
        )
        
        # Shockley-Ramo equation
        equation = MathTex(
            r"I = q \cdot \vec{v} \cdot \vec{E}_w",
            font_size=36
        ).to_corner(UL)
        
        # Velocity arrow (will be animated)
        velocity_arrow = always_redraw(
            lambda: Arrow(
                charge_group.get_center(),
                charge_group.get_center() + UP * 0.8,
                buff=0,
                color=GREEN,
                stroke_width=3
            )
        )
        velocity_label = always_redraw(
            lambda: MathTex(r"\vec{v}", font_size=28, color=GREEN).next_to(
                velocity_arrow, RIGHT, buff=0.1
            )
        )
        
        # Build the scene
        self.play(
            Create(top_electrode),
            Create(bottom_electrode),
            Write(top_label),
            Write(bottom_label),
            run_time=1.5
        )
        
        self.play(
            Create(circuit),
            Create(ammeter),
            Write(ammeter_label),
            run_time=1
        )
        
        self.play(
            *[GrowArrow(arrow) for arrow in field_lines],
            Write(field_label),
            run_time=1.5
        )
        
        self.play(Write(equation), run_time=1)
        
        self.play(
            FadeIn(charge_group),
            run_time=0.5
        )
        
        self.play(
            GrowArrow(velocity_arrow),
            Write(velocity_label),
            run_time=0.5
        )
        
        self.add(current_text)
        
        # Animate the charge moving and inducing current
        # For parallel plates: E_w = 1/d (uniform), so I = q*v/d
        # We'll show this as a normalized current
        
        def update_current(mob):
            # Current is proportional to velocity (which we keep constant here)
            # and inversely proportional to gap
            # Normalized to show ~1 when charge is moving
            y_pos = charge_group.get_center()[1]
            if start_y < y_pos < end_y:
                current_tracker.set_value(0.8)  # Constant current for uniform field
            else:
                current_tracker.set_value(0)
        
        charge_group.add_updater(update_current)
        
        # Main animation: charge moves from bottom to top
        self.play(
            charge_group.animate.move_to([0, end_y, 0]),
            run_time=4,
            rate_func=linear
        )
        
        charge_group.remove_updater(update_current)
        current_tracker.set_value(0)
        
        self.wait(0.5)
        
        # Show what happens when charge stops
        stop_text = Text("Charge stops → No current!", font_size=28, color=RED)
        stop_text.to_corner(DR)
        self.play(Write(stop_text), run_time=1)
        
        self.wait(1)
        
        # Move charge back down
        self.play(FadeOut(stop_text))
        
        reverse_text = Text("Reverse direction → Reverse current", font_size=28, color=ORANGE)
        reverse_text.to_corner(DR)
        self.play(Write(reverse_text))
        
        def update_current_reverse(mob):
            y_pos = charge_group.get_center()[1]
            if start_y < y_pos < end_y:
                current_tracker.set_value(-0.8)  # Negative current
            else:
                current_tracker.set_value(0)
        
        charge_group.add_updater(update_current_reverse)
        
        # Charge moves back down
        reverse_velocity = always_redraw(
            lambda: Arrow(
                charge_group.get_center(),
                charge_group.get_center() + DOWN * 0.8,
                buff=0,
                color=GREEN,
                stroke_width=3
            )
        )
        
        self.play(
            ReplacementTransform(velocity_arrow, reverse_velocity),
            run_time=0.3
        )
        
        self.play(
            charge_group.animate.move_to([0, start_y, 0]),
            run_time=4,
            rate_func=linear
        )
        
        charge_group.remove_updater(update_current_reverse)
        current_tracker.set_value(0)
        
        self.wait(2)


class ShockleyRamoDetailed(Scene):
    """
    More detailed version showing the weighting potential concept.
    """
    
    def construct(self):
        # Title
        title = Text("Shockley-Ramo Theorem", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP))
        
        # Explanation
        explanation = VGroup(
            Text("The induced current on an electrode is:", font_size=28),
            MathTex(r"I = -q \vec{v} \cdot \vec{E}_w", font_size=40),
            Text("where:", font_size=24),
            MathTex(r"q = \text{charge}", font_size=28),
            MathTex(r"\vec{v} = \text{charge velocity}", font_size=28),
            MathTex(r"\vec{E}_w = -\nabla \phi_w = \text{weighting field}", font_size=28),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        explanation.next_to(title, DOWN, buff=0.5)
        
        for item in explanation:
            self.play(Write(item), run_time=0.8)
        
        self.wait(2)
        
        # Clear and show weighting potential concept
        self.play(FadeOut(explanation))
        
        concept = VGroup(
            Text("Weighting Potential φ_w:", font_size=32, color=RED),
            Text("• Set sensing electrode to V = 1", font_size=24),
            Text("• Set all other electrodes to V = 0", font_size=24),
            Text("• Solve Laplace's equation ∇²φ_w = 0", font_size=24),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        concept.next_to(title, DOWN, buff=0.5)
        
        for item in concept:
            self.play(Write(item), run_time=0.6)
        
        self.wait(2)
        
        # Key insight
        insight = VGroup(
            Text("Key Insight:", font_size=32, color=GREEN),
            Text("Current depends ONLY on charge motion,", font_size=26),
            Text("NOT on the actual electric field!", font_size=26),
        ).arrange(DOWN, buff=0.2)
        insight.to_edge(DOWN, buff=1)
        
        self.play(Write(insight), run_time=2)
        self.wait(3)


if __name__ == "__main__":
    # To render: manim -pql shockley_ramo.py ShockleyRamoTheorem
    pass
